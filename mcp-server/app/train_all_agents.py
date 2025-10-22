# app/train_all_agents.py

from agents import contextAnalyzer, transactionHistoryProfiler, fraudPatternMatcher

def main():
    print("Training Agent 1: Initiation Context Analyzer...")
    model1 = contextAnalyzer.train_agent1()
    print("Agent 1 trained.")

    print("🔧 Training Agent 2: Transaction History Profiler...")
    model2 = transactionHistoryProfiler.train_agent2()
    print(" Agent 2 trained.")

    print(" Training Agent 4: Fraud Pattern Matcher...")
    model4 = fraudPatternMatcher.train_agent4()
    print(" Agent 4 trained.")

    # Optional: Save models to disk or cache here if needed
    # e.g., joblib.dump(model1, "models/agent1.pkl")

if __name__ == "__main__":
    main()
