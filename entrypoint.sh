# entrypoint.sh
#!/bin/bash
mkdir -p /app/data
aws s3 cp s3://dav-fraud-detection-bucket/ContextDataLogs/Cifer-Fraud-Detection-Dataset-AF-part-10-14.csv /app/data/device_ip_logs.csv
aws s3 cp s3://dav-fraud-detection-bucket/TransactionsHistoryLogs/transactions_context_data_logs_100k.csv /app/data/transaction_history.csv
exec "$@"
