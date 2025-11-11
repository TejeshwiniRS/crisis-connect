import os, json, requests
from datetime import datetime
from google.cloud import firestore, storage
from vertexai import init
from vertexai.preview.generative_models import GenerativeModel
from dotenv import load_dotenv

# --- Load .env if present (local only) ---
if os.path.exists(".env"):
    load_dotenv(".env")

PROJECT  = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
BUCKET   = os.getenv("REPORTS_BUCKET")
DATASCOUT = os.getenv("DATASCOUT_URL")
PLANNER   = os.getenv("RESOURCEPLANNER_URL")
SPEECH    = os.getenv("SPEECH_URL")

def fetch_data():
    db = firestore.Client(database="crisisconnect")
    inc = [d.to_dict() for d in db.collection("incidents").stream()]
    mat = [d.to_dict() for d in db.collection("matches").stream()]
    return inc, mat, db

def generate_report(incidents, matches):
    # 🔧 Convert Firestore timestamps to ISO strings
    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_clean(v) for v in obj]
        elif hasattr(obj, "isoformat"):  # handles DatetimeWithNanoseconds
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)
        return obj

    incidents = _clean(incidents)
    matches = _clean(matches)

    init(project=PROJECT, location=LOCATION)
    model = GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    Create a Markdown Situation Report from the following:
    INCIDENTS: {json.dumps(incidents)[:80000]}
    MATCHES: {json.dumps(matches)[:80000]}
    """
    return model.generate_content(prompt).text


def upload_to_gcs(content):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
    fname  = f"reports/{datetime.utcnow().strftime('%Y-%m-%d_%H-%M')}.md"
    blob   = bucket.blob(fname)
    blob.upload_from_string(content, content_type="text/markdown")
    return f"gs://{BUCKET}/{fname}"

def update_metadata(db, url):
    db.collection("metadata").document("latest_report").set({
        "timestamp": datetime.utcnow().isoformat(),
        "report_url": url,
        "datascout_url": DATASCOUT,
        "planner_url": PLANNER,
        "speech_url": SPEECH
    })

if __name__ == "__main__":
    incidents, matches, db = fetch_data()

    report = generate_report(incidents, matches)
    url = upload_to_gcs(report)
    update_metadata(db, url)
    print("✅ ReportWriter complete:", url)
