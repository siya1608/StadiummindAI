import os
import logging
from pathlib import Path
from google import genai
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiEmbeddings(Embeddings):
    """Custom LangChain Embeddings wrapper using the official Google GenAI SDK."""
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds a list of documents using gemini-embedding-2."""
        try:
            results = []
            for text in texts:
                response = self.client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=text
                )
                results.append(response.embeddings[0].values)
            return results
        except Exception as e:
            logger.error(f"Error embedding documents with Google GenAI SDK: {e}")
            raise e

    def embed_query(self, text: str) -> list[float]:
        """Embeds a single query string using gemini-embedding-2."""
        try:
            response = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error embedding query with Google GenAI SDK: {e}")
            raise e

class ChromaService:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.embeddings = None

    def initialize_embeddings(self) -> bool:
        """Initialize official Google GenAI embeddings client."""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY or GOOGLE_API_KEY is not set. Embeddings cannot be initialized.")
            return False
        try:
            self.embeddings = GeminiEmbeddings(api_key=settings.GEMINI_API_KEY)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize official Google GenAI embeddings: {e}")
            return False

    def initialize_vector_db(self, force_reindex: bool = False) -> bool:
        """Loads or creates the Chroma Vector DB with stadium knowledge."""
        if not self.initialize_embeddings():
            logger.error("Skipping Vector DB initialization due to missing embeddings configuration.")
            return False

        db_dir = Path(settings.CHROMA_DB_DIR)
        knowledge_file = Path(settings.STADIUM_KNOWLEDGE_PATH)

        # Check if we need to index
        db_exists = db_dir.exists() and any(db_dir.iterdir())
        
        if db_exists and not force_reindex:
            logger.info("Chroma DB directory exists and is not empty. Loading existing database...")
            try:
                self.vector_store = Chroma(
                    persist_directory=str(db_dir),
                    embedding_function=self.embeddings
                )
                self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                return True
            except Exception as e:
                logger.error(f"Error loading existing Chroma DB: {e}. Rebuilding...")

        # Build DB
        if not knowledge_file.exists():
            logger.error(f"Knowledge base file not found at {knowledge_file}")
            return False

        logger.info("Building Chroma DB from stadium_knowledge.txt...")
        try:
            with open(knowledge_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Split content by sections starting with "==="
            sections = content.split("===")
            documents = []
            
            # The first split might be empty or preamble
            if sections[0].strip():
                documents.append(Document(
                    page_content=sections[0].strip(),
                    metadata={"source": "stadium_overview"}
                ))

            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    section_title = sections[i].strip()
                    section_content = sections[i+1].strip()
                    documents.append(Document(
                        page_content=f"{section_title}\n{section_content}",
                        metadata={"source": section_title.lower().replace(" & ", "_").replace(" ", "_")}
                    ))

            # Re-create directory if forcing reindex
            if db_dir.exists() and force_reindex:
                import shutil
                shutil.rmtree(db_dir)
            db_dir.parent.mkdir(parents=True, exist_ok=True)

            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(db_dir)
            )
            
            # Persist vector store
            try:
                self.vector_store.persist()
            except AttributeError:
                pass
                
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            logger.info(f"Successfully indexed {len(documents)} knowledge sections into Chroma DB.")
            return True

        except Exception as e:
            logger.error(f"Failed to create Chroma DB: {e}")
            return False

    def retrieve_context(self, query: str) -> str:
        """Helper to retrieve string context matching a query."""
        if not self.retriever:
            logger.warning("Retriever not initialized. Cannot retrieve context.")
            return ""
        try:
            docs = self.retriever.invoke(query)
            context_str = "\n\n".join([doc.page_content for doc in docs])
            return context_str
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}")
            return ""

# Singleton instance
chroma_service = ChromaService()
