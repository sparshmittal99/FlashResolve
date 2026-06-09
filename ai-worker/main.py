import json
import redis
import time
import os
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("Missing GEMINI_API_KEY in .env file!")

# --- DYNAMIC NETWORKING FOR LOCAL DOCKER & CLOUD HOSTING ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_SSL_ENABLED = os.getenv("REDIS_SSL_ENABLED", "false").lower() == "true"

JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8081")
PORT = int(os.getenv("PORT", 10000))  # Render automatically injects PORT env variable
# -----------------------------------------------------------

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

class GraphState(TypedDict):
    transaction: dict
    risk_score: int
    explanation: str
    action: str

def analyze_transaction(state: GraphState):
    txn = state["transaction"]
    
    prompt = f"""
    You are an enterprise AI Fraud Risk Engine for 'FlashResolveAI'.
    Analyze this incoming transaction payload against a multi-factor risk matrix:
    
    TRANSACTION PAYLOAD:
    - Merchant ID: {txn.get('merchantId')}
    - Transaction Amount: ${txn.get('amount')}
    - Transaction Location: {txn.get('location', 'Unknown')}
    
    RISK EVALUATION MATRIX:
    1. GEOSPATIAL MISMATCH: Sudden international hops (+30 to risk score).
    2. VALUE ANOMALY: Large transactions over $500 (+40 to risk score).
    3. MERCHANT RISK TIERING: Marketplaces or high-risk keywords (+20 to risk score).

    Respond STRICTLY in a clean JSON object format. Use exactly these two keys:
    {{
      "risk_score": [Integer from 0 to 100],
      "explanation": "[A concise 1-2 sentence breakdown]"
    }}
    """
    
    response = llm.invoke(prompt)
    try:
        clean_text = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        return {"risk_score": int(result["risk_score"]), "explanation": result["explanation"]}
    except Exception:
        return {"risk_score": 85, "explanation": "AI optimization error. Flagged for review due to payload format issues."}

def decide_action(state: GraphState):
    score = state["risk_score"]
    if score > 75: action = "BLOCKED"
    elif score > 35: action = "FLAGGED"
    else: action = "APPROVED"
    return {"action": action}

workflow = StateGraph(GraphState)
workflow.add_node("analyze", analyze_transaction)
workflow.add_node("decide", decide_action)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "decide")
workflow.add_edge("decide", END)
ai_app = workflow.compile()

# --- LIGHTWEIGHT HTTP HEALTH CHECK SERVER FOR RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AI Brain is healthy and processing queues!")
        
    def log_message(self, format, *args):
        return # Suppress health check ping noise in logs

def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"🟢 Health Check Server listening on port {PORT}...")
    server.serve_forever()
# --------------------------------------------------------

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,
    ssl=REDIS_SSL_ENABLED, db=0, decode_responses=True, health_check_interval=30
)

def process_queue():
    print(f"🤖 FlashResolve AI Brain is online! Connected to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    
    while True:
        try:
            message = redis_client.brpop("anomaly_queue", timeout=5)
            if message:
                _, transaction_json = message
                transaction = json.loads(transaction_json)
                txn_id = transaction.get('id')
                
                print(f"\n📥 New Transaction Received: ID {txn_id}")
                initial_state = {"transaction": transaction}
                final_state = ai_app.invoke(initial_state)
                
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
        except Exception as e:
            if "Timeout" not in str(e):
                print(f"❌ Redis Connection Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    # Start the web health check server in a side thread so Render stays happy
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Run your Redis listener on the main thread
    process_queue()