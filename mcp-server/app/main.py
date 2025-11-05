from fastapi import FastAPI
from agents import agent1, agent2, agent3, aggregator
from models.schemas import TransactionInput
import boto3, os, joblib
from aggregator_router import router as aggregator_router

app = FastAPI()

# Global models
agent1_model = None
agent2_model = None
agent3_graph = None

# S3 config
REGION = os.getenv("AWS_REGION", "ca-central-1")
BUCKET_NAME = os.getenv("MODEL_BUCKET", "dav-fraud-detection-models")
s3 = boto3.client("s3", region_name=REGION)

LOCAL_MODEL_DIR = "models"
os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)

def download_latest_model(agent_prefix: str):
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"agents/{agent_prefix}/")
        if "Contents" not in response:
            print(f"No models found for {agent_prefix}")
            return None
        latest = max(response["Contents"], key=lambda x: x["LastModified"])
        key = latest["Key"]
        local_path = os.path.join(LOCAL_MODEL_DIR, os.path.basename(key))
        s3.download_file(BUCKET_NAME, key, local_path)
        print(f"Downloaded {key} → {local_path}")
        return joblib.load(local_path)
    except Exception as e:
        print(f"Failed to download {agent_prefix} model: {e}")
        return None

@app.on_event("startup")
def load_agents():
    global agent1_model, agent2_model, agent3_graph
    agent1_model = download_latest_model("agent1")
    agent2_model = download_latest_model("agent2")
    agent3_graph = download_latest_model("agent3") or agent3.load_merchant_graph()

@app.post("/score")
async def score_transaction(tx: TransactionInput):
    if not agent1_model or not agent2_model or not agent3_graph:
        return {"error": "Models not loaded. Please check training jobs."}
    s1 = agent1.evaluate_agent1(agent1_model, tx)
    s2 = agent2.evaluate_agent2(agent2_model, tx)
    s3 = agent3.evaluate_agent3(agent3_graph, tx)
    final_score, explanation = aggregator.aggregate([s1, s2, s3])
    return {"score": final_score, "explanation": explanation}
