import os
from fastapi import FastAPI, Body
from .agent import root_agent

app = FastAPI(title="datascout-adk")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/ingest/from_transcripts")
def ingest_from_transcripts(limit: int = 20):
    return root_agent.run_from_transcripts(limit=limit)

@app.post("/ingest/from_feed")
def ingest_from_feed(payload = Body(...)):
    items = payload.get("items", [])
    return root_agent.run_from_feed_items(items)
