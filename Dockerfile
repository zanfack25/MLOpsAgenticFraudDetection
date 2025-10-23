# -------------------------
# Dockerfile for EKS deployment
# -------------------------
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required by scientific libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    gfortran \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code into the image
COPY mcp-server/app/ ./app/

# Optional: expose port for API service
EXPOSE 8000

# Default command (can be overridden by Kubernetes Job)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
