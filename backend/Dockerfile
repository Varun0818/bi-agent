FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl sqlite3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Set environment for production paths
ENV DATABASE_URL=sqlite:///./data/app.db
ENV DEMO_DB_URL=sqlite:///./data/demo.db
ENV CHROMA_PATH=./data/chroma_store

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Init DB then start server
CMD ["sh", "-c", "python db/init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"]