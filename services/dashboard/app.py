from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from google.cloud import firestore
import httpx, os

app = FastAPI()
db  = firestore.Client()

SPEECH_URL = os.getenv("SPEECH_URL")  # speech-transcriber URL

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    incidents = [d.to_dict() for d in db.collection("matches").stream()]
    report = db.collection("metadata").document("latest_report").get().to_dict() or {}
    html = "<h1>CrisisConnect</h1><form method='post' enctype='multipart/form-data' action='/upload-audio'>" \
           "<input type='file' name='file'/><button>Transcribe</button></form>" \
           f"<p>Latest report: {report.get('report_url','(none)')}</p>" \
           "<h2>Active Incidents</h2><ul>" + "".join(
            f"<li>{i['incident'].get('location','?')} – {i['incident'].get('summary','')}</li>"
            for i in incidents
           ) + "</ul>"
    return html

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SPEECH_URL}/transcribe", files={"file": (file.filename, await file.read())})
    # After transcript, call datascout to summarize from transcripts
    async with httpx.AsyncClient() as client:
        await client.post(os.getenv("DATASCOUT_URL") + "/ingest/from_transcripts", json={"limit": 5})
    # And match
    async with httpx.AsyncClient() as client:
        await client.post(os.getenv("RESOURCEPLANNER_URL") + "/match")
    return {"ok": True}
