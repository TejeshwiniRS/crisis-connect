from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import firestore
from datetime import datetime
import httpx, os

app = FastAPI(title="CrisisConnect Dashboard")
db = firestore.Client(database="crisisconnect")

# Mount static assets + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Environment variables ---
DATASCOUT_URL = os.getenv("DATASCOUT_URL")
RESOURCEPLANNER_URL = os.getenv("RESOURCEPLANNER_URL")
CRISISSUMMARIZER_URL = os.getenv("CRISISSUMMARIZER_URL")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    report = db.collection("metadata").document("latest_report").get().to_dict() or {}
    if report.get("report_url", "").startswith("gs://"):
        _, _, bucket, *path = report["report_url"].split("/")
        blob_name = "/".join(path)
        report["report_url"] = f"https://storage.googleapis.com/{bucket}/{blob_name}"

    matches = [d.to_dict() for d in db.collection("matches").stream()]
    summary_doc = db.collection("summary").document("current").get().to_dict() or {}

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "matches": matches,
            "report": report,
            "summary": summary_doc.get("text", ""),
        },
    )


@app.post("/report-incident")
async def report_incident(
    location: str = Form(...),
    summary: str = Form(...),
    needs: str = Form("")
):
    incident = {
        "location": location,
        "summary": summary,
        "needs": [n.strip() for n in needs.split(",") if n.strip()],
        "timestamp": datetime.utcnow().isoformat(),
    }
    db.collection("incidents").document().set(incident)

    async with httpx.AsyncClient(timeout=300.0) as client:
        await client.post(f"{RESOURCEPLANNER_URL}/match")

    return RedirectResponse("/", status_code=303)


@app.get("/update-summary")
async def update_summary():
    """Call CrisisSummarizer to summarize the latest report."""
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(f"{CRISISSUMMARIZER_URL}/summarize_latest")
        summary_text = resp.text

    db.collection("summary").document("current").set({
        "text": summary_text,
        "updated_at": datetime.utcnow().isoformat()
    })
    return RedirectResponse("/", status_code=303)

@app.get("/refresh")
async def refresh():
    """Trigger DataScout & ResourcePlanner to reprocess recent data."""
    async with httpx.AsyncClient() as client:
        await client.post(f"{DATASCOUT_URL}/ingest/from_transcripts", json={"limit": 5})
        await client.post(f"{RESOURCEPLANNER_URL}/match")
    return RedirectResponse("/", status_code=303)
