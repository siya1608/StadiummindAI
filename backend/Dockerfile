# ============================================================
# StadiumMind AI — Production Dockerfile
# Targets: Railway / Render (backend FastAPI service)
# Assumes build context is the 'backend' directory (Root Directory)
# ============================================================

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy all files
COPY . .

# Ensure data & chroma directories exist
RUN mkdir -p /app/data/chroma_db

# Expose default port
EXPOSE 8000

# Start FastAPI app using the production-optimized run.py script
# This automatically reads $PORT from the environment (Railway/Railway)
CMD ["python3", "run.py"]

