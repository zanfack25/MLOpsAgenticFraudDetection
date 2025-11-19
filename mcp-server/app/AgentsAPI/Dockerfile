# ==========================================
# Dockerfile for FastAPI-based Agents API
# ==========================================

# Use a lightweight Python Base image
#==========================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Copy and install Python dependencies
# -----------------------------
COPY mcp-server/app/AgentsAPI/requirements.txt .

# Upgrade pip first, then install requirements
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Create directories used by agents
# -----------------------------
RUN mkdir -p /app/AgentsAPI/models
# -----------------------------
# Copy API source code
# -----------------------------
COPY mcp-server/app/AgentsAPI/ ./AgentsAPI/
COPY mcp-server/app/models/ ./AgentsAPI/models

# -----------------------------
# Set environment variables
# -----------------------------
# Force Python output to be unbuffered (useful for logging)
# Set default log level
ENV PYTHONUNBUFFERED=1 \
    UVICORN_LOG_LEVEL=info \
    MODEL_BUCKET=dav-fraud-detection-models \
    REGION=ca-central-1 \
    AWS_DEFAULT_REGION=ca-central-1

# -----------------------------
# Expose FastAPI port
# -----------------------------
EXPOSE 80

# -----------------------------
# Default command (production)
# -----------------------------
# Uvicorn’s reload watcher can break in Docker containers in production mode.
CMD ["uvicorn", "AgentsAPI.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
