# mcp-server/app/AgentsAPI/main.py
# ------------------------------------------------------------
# Main FastAPI entrypoint for all fraud detection agents
# ------------------------------------------------------------

from fastapi import FastAPI

# Import routers from each agent API
from AgentsAPI.aggregator_api import router as aggregator_router
from AgentsAPI.context_analyser_api import router as context_router
from AgentsAPI.fraud_pattern_matcher_api import router as matcher_router
from AgentsAPI.orchestrator_api import router as orchestrator_router
from AgentsAPI.transaction_history_profiler_api import router as profiler_router

# ------------------------------------------------------------
# Main FastAPI Application
# ------------------------------------------------------------
app = FastAPI(title="Fraud Detection API", docs_url="/docs", redoc_url="/redoc")

# Include routers under specific prefixes
app.include_router(aggregator_router, prefix="/aggregator", tags=["Aggregator"])
app.include_router(context_router, prefix="/context-analyser", tags=["Context Analyzer"])
app.include_router(matcher_router, prefix="/fraud-matcher", tags=["Fraud Pattern Matcher"])
app.include_router(profiler_router, prefix="/transaction-history", tags=["Transaction History Profiler"])
app.include_router(orchestrator_router, prefix="/orchestrator", tags=["Orchestrator"])

# ------------------------------------------------------------
# Root endpoint for sanity check / health check
# ------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Fraud Detection API is running. Check /docs for API documentation."}
