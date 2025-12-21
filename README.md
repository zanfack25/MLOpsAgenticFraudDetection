

## Solution Architecture Overview

![High-level architecture](docs/images/fraud-detection-aws-infrastructure.png)

## Business Use case 


# AWS Cloud-Based Agentic Fraud Detection & Response System

**Real-Time Banking Fraud Detection using Agentic AI, MLOps & Terraform IaC**

---

## Project Overview

This project implements a **cloud-native, real-time banking fraud detection system** using **Agentic AI**, **Machine Learning**, and **AWS Infrastructure as Code (Terraform)**.

Unlike traditional rule-based or static recommendation systems, this solution introduces a **Multi-Agent Control Plane (MCP)** that evaluates transactions **contextually and autonomously**, enabling **instant fraud prevention actions** such as blocking transactions, triggering MFA, or escalating to human analysts.

The system is designed to be:

* **Scalable** (millions of transactions/sec)
* **Adaptive** (continuous learning)
* **Explainable** (transparent AI decisions)
* **Compliant** (PCI DSS, FINTRAC, PIPEDA)

---

## Business Motivation

Financial institutions lose **over $12 billion annually** to fraud in Canada alone (LTC Report).
Traditional rule-based fraud systems:

* Fail to adapt to evolving fraud patterns
* Generate high false positives
* Require heavy human intervention

### This project addresses those limitations by:

* Using **AI agents** instead of static rules
* Applying **real-time ML inference**
* Automating **decision-making & response**
* Reducing **false positives** while increasing **precision**

---

## Key Concepts

* **Agentic AI**: Autonomous AI agents making contextual decisions
* **MLOps**: Continuous training, deployment, and monitoring
* **IaC (Terraform)**: Fully reproducible cloud infrastructure
* **Microservices and Event-driven architecture**
* **Explainable AI (XAI)** using SHAP

---

## System Capabilities

✔ Real-time transaction risk scoring
✔ Context-aware fraud detection
✔ Automated response (block, MFA, escalate)
✔ Continuous model learning
✔ Explainable decisions for auditors
✔ Analyst workload reduction

---

## Example Fraud Scenario

**Scenario**
A Toronto customer usually spends ~$200 locally.
A sudden $5,000 transaction is attempted from the Bahamas.

**System Response**

1. Transaction ingested via **API Gateway**
2. Streamed through **Amazon Kinesis**
3. ML model (SageMaker) outputs **risk score = 0.88**
4. Agent blocks transaction immediately
5. Customer notified via SMS & push notification
6. Customer feedback updates future model behavior
7. Full audit trail logged for compliance

✅ Fraud stopped
✅ Minimal customer friction
✅ Continuous system learning

---

## 🧱 Architecture Overview

```text
Client / Banking App
        |
   API Gateway
        |
   Redshift Stream
        |
+----------------------+
|  MCP Agent Server    |
|----------------------|
| Agent 1: Initiation  |
| Agent 2: History     |
| Agent 3: Destination |
| Agent 4: Pattern     |
| Agent 5: Aggregator  |
+----------------------+
        |
 Decision Engine
        |
  ├─ Block Transaction
  ├─ Trigger MFA
  ├─ Escalate to Analyst
        |
 Logs & Monitoring
```

---

##  Multi-Agent Control Plane (MCP)

### Agent Responsibilities

###  Agent 1 – Transaction Initiation Context Analyzer

* **Purpose**: Detect anomalies at transaction entry
* **Inputs**: IP, device ID, geolocation, timestamp
* **Model**: Isolation Forest / Autoencoder
* **Output**: `transaction_initiation_context_score`
* **Tech**: Python, Scikit-learn, FastAPI

---

###  Agent 2 – Transaction History Profiler

* **Purpose**: Compare amount & behavior vs customer history
* **Inputs**: Historical transactions, spending habits
* **Model**: Time Series Forecasting + Clustering
* **Output**: `transaction_history_score`
* **Tech**: PyTorch, Prophet, PostgreSQL

---

###  Agent 3 – Destination Risk Evaluator

* **Purpose**: Assess merchant, receiver bank trust
* **Inputs**: Merchant ID, bank, payment provider
* **Model**: Graph Neural Network (GNN)
* **Output**: `transaction_destination_context_score`
* **Tech**: Neo4j, PyTorch Geometric

---

###  Agent 4 – Fraud Pattern Matcher

* **Purpose**: Match against known fraud patterns
* **Inputs**: Metadata, fraud knowledge base
* **Model**: XGBoost + NLP (BERT)
* **Output**: `transaction_pattern_score`
* **Tch**: Elasticsearch, HuggingFace

---

### Agent 5 – Risk Aggregator & Decision Engine

* **Purpose**: Final decision-making & explainability
* **Inputs**: Scores from Agents 1–4
* **Model**: Weighted Ensemble + SHAP
* **Output**:

  * `transaction_risk_score`
  * Decision & recommendation
* **Tech**: Python, Flask, SHAP, Kafka

---

## Cloud Infrastructure (AWS)

### Compute

* **EKS** – Model training & experimentation
* **ECS Fargate** – Auto-scaling inference services
* **Lambda** – Event-driven agent orchestration
* **ALB** – Load balancing

### Data

* **Amazon S3** – Model storage (`fraud-detection-models`)
* **Amazon Redshift** – Transaction warehouse
* **Neo4j** – Graph trust relationships
* **Redis** – Low-latency caching

### Streaming & Messaging

* **Amazon Kinesis** – Real-time ingestion
* **Kafka / SQS** – Agent communication

---

## Security & Compliance

✔ PCI DSS
✔ FINTRAC AML/KYC
✔ PIPEDA

### Security Features

* IAM least-privilege roles
* VPC isolation
* TLS encryption
* S3 encryption at rest (SSE-S3)
* CloudTrail audit logs
* MFA via Cognito

---

##  Infrastructure as Code (Terraform)

All infrastructure is deployed using **Terraform**, ensuring:

* Reproducibility
* Version control
* Automated provisioning

**Terraform covers**:

* VPC & networking
* ECS / EKS clusters
* IAM roles
* Load balancers
* Storage & monitoring

---

##  Model Training & MLOps

* **Training**: EKS cluster
* **Model registry**: Amazon S3
* **Evaluation metrics** stored with models
* **CI/CD** for agent deployment
* Continuous feedback loop from customer responses

---

## 🖥️ Backend & Frontend

### Backend

* **FastAPI & Node.js**
* Real-time model invocation
* Agent orchestration APIs

### Frontend

* **Node.js + Flask**
* Transaction dashboard
* Fraud analytics by region
* Real-time alerts

---

##  Observability

* **CloudWatch Dashboards**
* Transaction anomaly tracking
* Fraud rate metrics
* Compliance alerts
* System health monitoring

---

##  Future Improvements

* Integrate **Generative AI (GPT / DeepSeek)** for:

  * Analyst query interface
  * Fraud explanation narratives
* Advanced reinforcement learning for agent policies
* Cross-bank fraud intelligence sharing
* Real-time adaptive thresholds

---

##  Conclusion

This project demonstrates how **Agentic AI + Cloud MLOps** can transform banking fraud detection from **passive monitoring** into **active, intelligent defense**.

By combining:

* Multi-agent AI
* Real-time ML inference
* Explainable decisions
* Terraform-based cloud automation

The system achieves **higher precision, lower false positives, improved customer trust**, and **operational efficiency**.

---

## 📄 License

MIT License

---

## Author

**[David Roland Gnimpieba Zanfack]**
Cloud Computing & AI Engineer
AWS | MLOps | Agentic AI | Terraform

---
