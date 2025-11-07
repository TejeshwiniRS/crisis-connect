from fastapi import FastAPI
from .agent import root_agent

app = FastAPI(title="resourceplanner-adk")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/match")
def do_match():
    return root_agent.plan()
