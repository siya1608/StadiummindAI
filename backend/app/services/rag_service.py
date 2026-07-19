"""
rag_service.py — Full LangChain + ChromaDB RAG Pipeline for StadiumMind AI
============================================================================
Uses:
  - LangChain DirectoryLoader + TextLoader / UnstructuredMarkdownLoader
  - RecursiveCharacterTextSplitter for intelligent chunking
  - GeminiEmbeddings (official google-genai SDK) for vector embeddings
  - ChromaDB as persistent vector store
  - Custom prompt template + Gemini 2.5 Flash for grounded answer generation

Flow:
  User Query
      │
      ▼
  Semantic Search (ChromaDB) ──► Top-K Chunks Retrieved
      │
      ▼
  Prompt Template (System + Context + History + Query)
      │
      ▼
  Gemini 2.5 Flash ──► Grounded Natural Language Response
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# RAG Prompt Template
# ---------------------------------------------------------------------------
RAG_SYSTEM_PROMPT = """You are StadiumMind AI, the official intelligent operations assistant for MetLife Stadium during the FIFA World Cup 2026.

Your role is to assist stadium operators, security teams, medical staff, and fans with clear, accurate, and actionable information about:
- Seating, gates, and directions
- Concessions, food options, and dietary needs
- Accessibility, elevators, and wheelchair routes
- Emergency procedures, medical zones, and security protocols
- Transport, parking, and transit schedules
- Stadium rules, entry requirements, and prohibited items

INSTRUCTIONS:
1. Use ONLY the retrieved context below to answer. Do not fabricate information.
2. If the context does not fully answer the question, say so clearly and provide what you can.
3. Be concise, professional, and precise. Use bullet points for multi-step answers.
4. Always reference specific section numbers, gate names, or zone identifiers from the context.
5. Maintain a calm, authoritative "mission control" tone appropriate for stadium operations.

LANGUAGE RULE (MANDATORY):
- Automatically detect the language of the user's question.
- Respond ENTIRELY in that same language — including all labels, directions, and bullet points.
- Do NOT switch to English if the user wrote in another language.
- Examples: if user writes in Spanish → respond in Spanish; Arabic → Arabic; French → French.

RETRIEVED CONTEXT:
{context}
"""

RAG_USER_TEMPLATE = """Question: {question}"""


class RAGService:
    """
    Full LangChain + ChromaDB Retrieval-Augmented Generation pipeline.
    Handles document loading, chunking, embedding, storage, retrieval, and generation.
    """

    def __init__(self):
        self.vector_store: Optional[Chroma] = None
        self.embeddings = None
        self.is_ready: bool = False
        self._data_dir = Path(settings.BASE_DIR) / "data"
        self._db_dir = Path(settings.CHROMA_DB_DIR)

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(self, force_reindex: bool = False) -> bool:
        """
        Full initialization: set up embeddings, load documents, build vector store.
        Returns True if successful, False if API key is missing or a fatal error occurs.
        """
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "RAGService: GEMINI_API_KEY is not set. RAG pipeline will run in mock mode."
            )
            return False

        try:
            # Step 1: Initialize Gemini embeddings
            if not self._init_embeddings():
                return False

            # Step 2: Load or build vector store
            db_exists = self._db_dir.exists() and any(self._db_dir.iterdir())

            if db_exists and not force_reindex:
                logger.info("RAGService: Loading existing ChromaDB from disk...")
                self._load_existing_db()
            else:
                logger.info("RAGService: Building ChromaDB from /data documents...")
                documents = self._load_and_split_documents()
                if not documents:
                    logger.error("RAGService: No documents found in /data folder. Aborting.")
                    return False
                self._build_vector_store(documents)

            self.is_ready = True
            logger.info(
                f"RAGService: Ready. Vector store loaded at '{self._db_dir}'."
            )
            return True

        except Exception as e:
            logger.error(f"RAGService: Initialization failed — {e}", exc_info=True)
            return False

    def _init_embeddings(self) -> bool:
        """Initialize the GeminiEmbeddings wrapper (uses official google-genai SDK)."""
        try:
            # Import here to avoid circular dependencies
            from app.services.chroma_service import GeminiEmbeddings
            self.embeddings = GeminiEmbeddings(api_key=settings.GEMINI_API_KEY)
            logger.info("RAGService: GeminiEmbeddings initialized (text-embedding-004).")
            return True
        except Exception as e:
            logger.error(f"RAGService: Failed to init embeddings — {e}")
            return False

    # ------------------------------------------------------------------
    # Document Loading & Chunking
    # ------------------------------------------------------------------

    def _load_and_split_documents(self) -> List[Document]:
        """
        Uses LangChain DirectoryLoader to load all .txt and .md files from /data.
        Then splits them into chunks using RecursiveCharacterTextSplitter.
        """
        all_docs: List[Document] = []

        # Load .txt files
        txt_loader = DirectoryLoader(
            str(self._data_dir),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=False,
            use_multithreading=False,
            silent_errors=True,
        )
        # Load .md files
        md_loader = DirectoryLoader(
            str(self._data_dir),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=False,
            use_multithreading=False,
            silent_errors=True,
        )

        for loader in [txt_loader, md_loader]:
            try:
                docs = loader.load()
                all_docs.extend(docs)
                logger.info(f"RAGService: Loaded {len(docs)} document(s) via {loader.__class__.__name__}.")
            except Exception as e:
                logger.warning(f"RAGService: Loader error — {e}")

        if not all_docs:
            logger.error(f"RAGService: No documents loaded from {self._data_dir}")
            return []

        # Add source file name as metadata for citation
        for doc in all_docs:
            if doc.metadata.get("source"):
                doc.metadata["file"] = Path(doc.metadata["source"]).name

        logger.info(f"RAGService: Total raw documents loaded: {len(all_docs)}")

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,       # Optimal for Gemini embedding context
            chunk_overlap=150,    # Preserve cross-boundary context
            separators=["\n\n", "\n", "===", "---", "##", "#", ". ", " "],
            length_function=len,
        )
        chunks = splitter.split_documents(all_docs)
        logger.info(
            f"RAGService: Split {len(all_docs)} document(s) into {len(chunks)} chunks "
            f"(chunk_size=800, overlap=150)."
        )
        return chunks

    # ------------------------------------------------------------------
    # Vector Store
    # ------------------------------------------------------------------

    def _build_vector_store(self, chunks: List[Document]) -> None:
        """Embeds all chunks and persists them in ChromaDB."""
        # Clean up old DB if rebuilding
        if self._db_dir.exists():
            import shutil
            shutil.rmtree(self._db_dir)
            logger.info("RAGService: Removed stale ChromaDB directory for rebuild.")

        self._db_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"RAGService: Embedding {len(chunks)} chunks into ChromaDB...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self._db_dir),
            collection_name="stadium_knowledge",
        )

        # Persist (for older chromadb versions)
        try:
            self.vector_store.persist()
        except AttributeError:
            pass  # Newer chromadb versions persist automatically

        logger.info(
            f"RAGService: Successfully indexed {len(chunks)} chunks into ChromaDB at '{self._db_dir}'."
        )

    def _load_existing_db(self) -> None:
        """Loads an existing ChromaDB vector store from disk."""
        self.vector_store = Chroma(
            persist_directory=str(self._db_dir),
            embedding_function=self.embeddings,
            collection_name="stadium_knowledge",
        )
        count = self.vector_store._collection.count()
        logger.info(f"RAGService: Loaded existing ChromaDB with {count} vectors.")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve_context(self, query: str, k: int = 4) -> tuple[str, List[str]]:
        """
        Retrieves top-K semantically relevant document chunks for a query.

        Returns:
            (context_string, list_of_source_filenames)
        """
        if not self.vector_store:
            logger.warning("RAGService: Vector store not initialized. Returning empty context.")
            return "", []

        try:
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
            # Filter out very low-confidence chunks (score < 0.3)
            filtered = [(doc, score) for doc, score in results if score > 0.3]

            if not filtered:
                # Fall back to unfiltered if nothing passes threshold
                filtered = results[:2]

            chunks = [doc for doc, _ in filtered]
            context = "\n\n---\n\n".join([doc.page_content for doc in chunks])
            sources = list(set([
                doc.metadata.get("file", doc.metadata.get("source", "stadium_knowledge"))
                for doc in chunks
            ]))
            return context, sources

        except Exception as e:
            logger.error(f"RAGService: Retrieval error for query '{query}': {e}")
            return "", []

    # ------------------------------------------------------------------
    # Generation (RAG Full Pipeline)
    # ------------------------------------------------------------------

    def query(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        k: int = 4,
        detected_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline: Retrieve → Augment → Generate.

        Args:
            question: The user's natural language question.
            history: List of prior chat turns [{"role": "user"/"assistant", "content": "..."}]
            k: Number of chunks to retrieve from ChromaDB.
            detected_language: Optional explicit language name to force response language.

        Returns:
            {
                "response": str,       — Gemini's grounded answer
                "sources": list[str],  — Source filenames cited
                "chunks_used": int,    — Number of retrieved chunks
                "mode": str            — "rag" or "mock"
            }
        """
        # --- Mock mode (no API key) ---
        if not self.is_ready:
            return {
                "response": (
                    "⚠️ StadiumMind AI is running in **offline mock mode** because the Gemini API key is not configured.\n\n"
                    "To enable full AI capabilities:\n"
                    "1. Get your key at https://aistudio.google.com/app/apikey\n"
                    "2. Open `backend/.env` and set `GEMINI_API_KEY=your_key_here`\n"
                    "3. Restart the backend server."
                ),
                "sources": [],
                "chunks_used": 0,
                "mode": "mock",
            }

        # --- Step 1: Retrieve relevant chunks ---
        context, sources = self.retrieve_context(question, k=k)
        chunks_used = len(sources)

        # --- Step 2: Build prompt ---
        system_prompt = RAG_SYSTEM_PROMPT.format(
            context=context if context else "No relevant context was found in the knowledge base. Answer using general knowledge."
        )
        # If an explicit language override is provided, reinforce it
        if detected_language and detected_language.lower() != "english":
            system_prompt += f"\n\nIMPORTANT: The user is communicating in {detected_language}. Your ENTIRE response MUST be in {detected_language}."

        # --- Step 3: Build conversation contents ---
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            contents = []
            if history:
                for turn in history:
                    role = "user" if turn.get("role") == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=turn.get("content", ""))]
                        )
                    )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=question)]
                )
            )

            # --- Step 4: Call Gemini 2.5 Flash ---
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                max_output_tokens=1024,
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=config,
            )

            return {
                "response": response.text,
                "sources": sources,
                "chunks_used": chunks_used,
                "mode": "rag",
            }

        except Exception as e:
            logger.error(f"RAGService: Generation failed — {e}", exc_info=True)
            return {
                "response": f"I encountered an error generating the response: {e}",
                "sources": sources,
                "chunks_used": chunks_used,
                "mode": "error",
            }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def reindex(self) -> bool:
        """Forces a full re-indexing of all documents in /data."""
        logger.info("RAGService: Forcing full re-index of /data documents...")
        self.is_ready = False
        return self.initialize(force_reindex=True)

    def get_status(self) -> Dict[str, Any]:
        """Returns current RAG pipeline status for health checks."""
        vector_count = 0
        if self.vector_store:
            try:
                vector_count = self.vector_store._collection.count()
            except Exception:
                pass

        data_files = []
        if self._data_dir.exists():
            data_files = [
                f.name for f in self._data_dir.iterdir()
                if f.suffix in (".txt", ".md", ".pdf")
            ]

        return {
            "is_ready": self.is_ready,
            "vector_count": vector_count,
            "db_path": str(self._db_dir),
            "data_directory": str(self._data_dir),
            "loaded_documents": data_files,
            "embeddings_model": "gemini-embedding-2",
            "llm_model": "gemini-2.0-flash",
        }


# Singleton instance
rag_service = RAGService()
