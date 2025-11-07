from google.cloud import firestore, storage
from vertexai import init
from vertexai.preview.generative_models import GenerativeModel
from datetime import datetime
import json, os

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
BUCKET  = os.getenv("REPORTS_BUCKET", f"{PROJECT}-crisis-reports")

def fetch(db):
    incidents = [d.to_dict() for d in db.collection("incidents").stream()]
    matches   = [d.to_dict() for d in db.collection("matches").stream()]
    images    = [d.to_dict() for d in db.collection("image_insights").stream()]  # optional
    return incidents, matches, images

def generate_markdown(incidents, matches, images):
    init(project=PROJECT, location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    model = GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Create a concise Markdown Situation Report from these data:
    INCIDENTS: {json.dumps(incidents)[:120000]}
    MATCHES: {json.dumps(matches)[:120000]}
    IMAGE_INSIGHTS: {json.dumps(images)[:120000]}
    Format with per-region sections and bullet points for needs & matched NGOs.
    """
    return model.generate_content(prompt).text

def upload(markdown: str):
    storage_client = storage.Client()
    bkt = storage_client.bucket(BUCKET)
    name = f"reports/{datetime.utcnow().strftime('%Y-%m-%d_%H-%M')}.md"
    b = bkt.blob(name)
    b.upload_from_string(markdown, content_type="text/markdown")
    return f"gs://{BUCKET}/{name}"

def save_meta(db, url):
    db.collection("metadata").document("latest_report").set({
        "timestamp": datetime.utcnow().isoformat(),
        "report_url": url
    })

if __name__ == "__main__":
    db = firestore.Client(database="crisisconnect")
    inc, mat, img = fetch(db)
    md = generate_markdown(inc, mat, img)
    url = upload(md)
    save_meta(db, url)
    print("Report:", url)
