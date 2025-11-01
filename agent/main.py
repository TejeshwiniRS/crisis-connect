from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests, os, redis, json, time

app = FastAPI(title="CrisisConnect Agent Service")

# --- Environment variables ---
NIM_LLM_ENDPOINT = os.getenv("NIM_LLM_ENDPOINT", "http://nemotron-nano:8000/infer")
NIM_EMB_ENDPOINT = os.getenv("NIM_EMB_ENDPOINT", "http://embedding-nim:8000/embeddings")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# --- Pydantic model ---
class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {"status": "Agent Service Running"}

@app.post("/ask")
def ask_agent(q: Query):
    cached = r.get(q.question)
    if cached:
        return {"answer": cached.decode(), "cached": True}

    # Step 1: Get question embedding
    emb_resp = requests.post(NIM_EMB_ENDPOINT, json={"text": q.question})
    embedding = emb_resp.json().get("embedding")

    # Step 2: Use that to query vector DB / dummy docs for now
    context = "Emergency Response Manual: Stay calm, assess safety, and call for help."

    # Step 3: Send to LLM NIM
    payload = {
        "inputs": f"Context: {context}\nQuestion: {q.question}",
        "parameters": {"temperature": 0.7}
    }
    start = time.time()
    llm_resp = requests.post(NIM_LLM_ENDPOINT, json=payload)
    end = time.time()

    answer = llm_resp.json().get("text", "Unable to generate answer.")
    latency = round(end - start, 3)

    # Log and cache
    r.set(q.question, answer, ex=3600)
    r.lpush("agent.logs", json.dumps({"q": q.question, "latency": latency}))

    return {"answer": answer, "cached": False, "latency": latency}
