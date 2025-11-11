from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
from google.cloud import firestore
import tempfile, os

app = FastAPI()
db = firestore.Client(database=os.getenv("GOOGLE_CLOUD_FIRESTORE_DB", "crisisconnect"))


MODEL_SIZE = os.getenv("MODEL_SIZE", "large-v3")
DEVICE     = "cuda" if os.getenv("CUDA_VISIBLE_DEVICES", "") != "" else "cpu"
COMPUTE    = "auto"  # uses float16 on GPU when available

model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE)

@app.get("/healthz")
def health():
    return {"ok": True, "device": DEVICE, "model": MODEL_SIZE}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        segments, info = model.transcribe(tmp.name)
    text = " ".join([seg.text for seg in segments])

    db.collection("transcripts").add({
        "text": text,
        "filename": file.filename,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    return {"transcript": text}
