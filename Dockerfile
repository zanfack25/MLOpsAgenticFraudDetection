# Dockerfile for EKS deployment with preloaded datasets
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
# Environment variable for dataset bucket
ARG DATA_BUCKET="dav-fraud-detection-bucket"
ENV DATA_BUCKET=${DATA_BUCKET}

# Create data directory
RUN mkdir -p /app/data

# Download all datasets from S3 into container
RUN aws s3 cp s3://${DATA_BUCKET}/ContextDataLogs/Cifer-Fraud-Detection-Dataset-AF-part-10-14.csv /app/data/device_ip_logs.csv && \
    aws s3 cp s3://${DATA_BUCKET}/TransactionsHistoryLogs/transactions_context_data_logs_100k.csv /app/data/transaction_history.csv

# Verify dataset presence (optional)
RUN ls -lh /app/data
# Make sure Python can find the app module
ENV PYTHONPATH=/app

# Open http port for API service call
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
