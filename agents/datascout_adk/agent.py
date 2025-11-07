# Minimal ADK-style agent that uses Gemini via Vertex AI to structure text.
from typing import Dict, Any, List
import json, os
from google.cloud import firestore
from vertexai import init
from vertexai.preview.generative_models import GenerativeModel


# ADK base class pattern
class DataScoutAgent:
    def __init__(self):
        init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
        self.model = GenerativeModel("gemini-1.5-flash")
        self.db = firestore.Client(database="crisisconnect")


    def summarize_text(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        Read this disaster update and output compact JSON with keys:
        location, disaster_type, summary, needs (array of strings).
        Text: ```{text}```
        """
        resp = self.model.generate_content(prompt)
        # Be defensive if model returns Markdown fence
        content = resp.text.strip().strip("```").strip()
        try:
            obj = json.loads(content)
        except Exception:
            # fallback: wrap into a minimal record
            obj = {"location": "unknown", "disaster_type": "unknown", "summary": content, "needs": []}
        return obj

    def run_from_transcripts(self, limit: int = 20) -> Dict[str, Any]:
        # Pull latest speech transcripts and create incidents
        docs = (
            self.db.collection("transcripts")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        count = 0
        for d in docs:
            text = d.to_dict().get("text", "")
            if not text:
                continue
            inc = self.summarize_text(text)
            self.db.collection("incidents").add(inc)
            count += 1
        return {"created": count}

    def run_from_feed_items(self, feed_items: List[str]) -> Dict[str, Any]:
        # For RSS/news strings already fetched by your dashboard or a cron
        count = 0
        for raw in feed_items:
            inc = self.summarize_text(raw)
            self.db.collection("incidents").add(inc)
            count += 1
        return {"created": count}

# ADK expects a top-level agent variable:
root_agent = DataScoutAgent()
