FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies with vanna <2.0 to match existing code
RUN uv pip install --system --no-cache \
    anthropic>=0.69.0 \
    chromadb>=1.1.1 \
    mcp>=1.16.0 \
    paramiko==2.12.0 \
    pymysql>=1.1.2 \
    python-dotenv>=1.1.1 \
    sshtunnel==0.4.0 \
    "vanna[chromadb,ollama]<2.0" \
    starlette \
    uvicorn

# Copy application files
COPY main.py ./

# Create chroma data directory
RUN mkdir -p /app/chroma_data

CMD ["python", "main.py"]
