import json
import redis
import time
import os
import requests
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("Missing GEMINI_API_KEY in .env file!")

# --- DYNAMIC NETWORKING FOR DOCKER ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8081")
# -------------------------------------

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

class GraphState(TypedDict):
    transaction: dict
    risk_score: int
    explanation: str
    action: str

def analyze_transaction(state: GraphState):
    txn = state["transaction"]
    
    # 🚀 Extracted real-world contextual metrics to feed into the prompt
    prompt = f"""
    You are an enterprise AI Fraud Risk Engine for 'FlashResolveAI'.
    Analyze this incoming transaction payload against a multi-factor risk matrix:
    
    TRANSACTION PAYLOAD:
    - Merchant ID: {txn.get('merchantId')}
    - Transaction Amount: ${txn.get('amount')}
    - Transaction Location: {txn.get('location', 'Unknown')}
    
    RISK EVALUATION MATRIX:
    
    1. GEOSPATIAL MISMATCH:
       - Low Risk: Local or domestic transactions matching a standard baseline.
       - High Risk: Sudden international hops or cross-border locations (e.g., a user account shifting suddenly to Dublin, Ireland, or offshore regions) without a prior baseline. Significant weight should be added (+30 to risk score).
       
    2. VALUE ANOMALY (Average Order Value Deviation):
       - Low Risk: Retail amounts under $100.
       - Medium Risk: Everyday amounts between $100 and $500.
       - High Risk: Large transactions over $500 (+40 to risk score). Combined with international or high-risk merchants, this is an automatic trigger for high fraud flags.
       
    3. MERCHANT RISK TIERING:
       - Low Risk: Groceries, utilities, insurance, standard subscriptions.
       - Medium/High Risk: Massive online marketplaces (Amazon, eBay) for high-resale electronics, or high-risk keywords like 'CRYPTO', 'CASINO', 'UNKNOWN', or digital asset transfers (+20 to risk score).

    DECISION & OUTPUT SCORING SCALES:
    - Compute a total weighted score strictly between 0 and 100.
    
    Respond STRICTLY in a clean JSON object format. Do not add markdown wrappers. Use exactly these two keys:
    {{
      "risk_score": [Integer from 0 to 100],
      "explanation": "[A concise 1-2 sentence breakdown citing the explicit geospatial, merchant, or value risks driven by the payload]"
    }}
    """
    
    response = llm.invoke(prompt)
    
    try:
        # Clean markdown wrappers if returned by the model
        clean_text = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        return {"risk_score": int(result["risk_score"]), "explanation": result["explanation"]}
    except Exception:
        # Fallback processing safety
        return {"risk_score": 85, "explanation": "AI optimization error. Flagged for review due to payload format issues."}

def decide_action(state: GraphState):
    score = state["risk_score"]
    
    # Real-world risk tier mapping
    if score > 75:
        action = "BLOCKED"
    elif score > 35:
        action = "FLAGGED"
    else:
        action = "APPROVED"
        
    return {"action": action}

workflow = StateGraph(GraphState)
workflow.add_node("analyze", analyze_transaction)
workflow.add_node("decide", decide_action)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "decide")
workflow.add_edge("decide", END)

ai_app = workflow.compile()

# Using the dynamic REDIS_HOST
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True, health_check_interval=30)

def process_queue():
    print(f"🤖 FlashResolve AI Brain is online! Connected to Redis at {REDIS_HOST}...")
    
    while True:
        try:
            message = redis_client.brpop("anomaly_queue", timeout=5)
            
            if message:
                _, transaction_json = message
                transaction = json.loads(transaction_json)
                txn_id = transaction.get('id')
                
                print(f"\n📥 New Transaction Received: ID {txn_id}")
                print(f"   Merchant: {transaction.get('merchantId')} | Amount: ${transaction.get('amount')} | Location: {transaction.get('location', 'Unknown')}")
                print("   🧠 AI is evaluating against multi-factor risk models...")
                
                initial_state = {"transaction": transaction}
                final_state = ai_app.invoke(initial_state)
                
                print(f"   📊 Risk Score: {final_state['risk_score']}/100")
                print(f"   📝 Reason: {final_state['explanation']}")
                print(f"   🎯 Decision: {final_state['action']}")
                
                try:
                    update_payload = {
                        "riskScore": final_state['risk_score'],
                        "aiExplanation": final_state['explanation'],
                        "status": final_state['action']
                    }
                    webhook_url = f"{JAVA_API_URL}/api/transactions/{txn_id}/result"
                    requests.put(webhook_url, json=update_payload)
                    print("   💾 Successfully saved AI decision to PostgreSQL via Java!")
                except Exception as db_err:
                    print(f"   ⚠️ Could not save to database: {db_err}")
                
                print("-" * 50)

        except Exception as e:
            if "Timeout" not in str(e):
                print(f"❌ Redis Connection Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    process_queue()