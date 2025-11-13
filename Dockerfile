# Dockerfile for EKS deployment with preloaded datasets --
# Updated version
#===========================+++++++++++
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    gfortran \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
# Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY mcp-server/app/ ./


# Preload datasets from S3 into the image
# Dockerfile
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Make sure Python can find the app module
ENV PYTHONPATH=/app

# Open http port for API service call
EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000"]
