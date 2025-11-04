# ==========================================
# Dockerfile for FastAPI-based Agents API
# ==========================================

# Base Image
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install API-specific requirements
COPY mcp-server/app/AgentsAPI/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY mcp-server/app/AgentsAPI/ ./AgentsAPI/

# Expose the API port
EXPOSE 8000

# Default command
CMD ["uvicorn", "AgentsAPI.orchestrator_api:app", "--host", "0.0.0.0", "--port", "8000"]

