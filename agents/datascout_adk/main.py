# emulates adk.http.serve
from fastapi import FastAPI, Request
from agent import root_agent

app = FastAPI()

@app.get("/healthz")
def health():
    return {"ok": True, "agent": root_agent.name}

@app.post("/invoke/{action}")
async def invoke(action: str, request: Request):
    """
    Mimics ADK's /invoke/<action> endpoint.
    Expects JSON body and dispatches to @action() methods.
    """
    data = await request.json()
    if not hasattr(root_agent, action):
        return {"error": f"unknown action {action}"}
    fn = getattr(root_agent, action)
    try:
        result = fn(**data)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
