# ==========================================
# Dockerfile for FastAPI-based Agents API
# ==========================================

# Use a lightweight Python image
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
# Copy API source code
# -----------------------------
COPY mcp-server/app/AgentsAPI/ ./AgentsAPI/

# -----------------------------
# Set environment variables
# -----------------------------
# Force Python output to be unbuffered (useful for logging)
ENV PYTHONUNBUFFERED=1
# Set default log level
ENV UVICORN_LOG_LEVEL=info

# -----------------------------
# Expose FastAPI port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Default command (production)
# -----------------------------
CMD ["uvicorn", "AgentsAPI.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--reload"]
