# Updated and enhanced main.py that ensures each agent is trained
# before evaluation. It uses FastAPI’s startup event to train models once
# when the server launches,
# and then uses those trained models for scoring incoming transactions.
#
# - Trains agents once at startup using FastAPI’s @on_event("startup").
#
# - Stores trained models and graph in global variables.
#
# - Removes Agent 4 (Fraud Pattern Matcher) since it was deprecated.
#
# - Ensures consistent and efficient scoring pipeline.


from fastapi import FastAPI
from app.agents import agent1, agent2, agent3, aggregator
from app.models.schemas import TransactionInput

app = FastAPI()

# Global models for agents
agent1_model = None
agent2_model = None
agent3_graph = None

@app.on_event("startup")
def train_agents():
    global agent1_model, agent2_model, agent3_graph
    agent1_model = agent1.train_agent1()
    agent2_model = agent2.train_agent2()
    agent3_graph = agent3.load_merchant_graph()

@app.post("/score")
async def score_transaction(tx: TransactionInput):
    s1 = agent1.evaluate_agent1(agent1_model, tx)
    s2 = agent2.evaluate_agent2(agent2_model, tx)
    s3 = agent3.evaluate_agent3(agent3_graph, tx)
    final_score, explanation = aggregator.aggregate([s1, s2, s3])
    return {"score": final_score, "explanation": explanation}
