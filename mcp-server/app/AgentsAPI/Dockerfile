# ==========================================
# Dockerfile for FastAPI-based Agents API
# ==========================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the orchestrator (entrypoint API)
CMD ["uvicorn", "orchestrator_api:app", "--host", "0.0.0.0", "--port", "8000"]
