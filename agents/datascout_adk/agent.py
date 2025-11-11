from typing import Dict, Any, List, Optional
import os, json
from google.cloud import firestore
from vertexai import init
from vertexai.preview.generative_models import GenerativeModel
from adk import Agent, action
import feedparser


# Optional imports for fallback HTTP dispatch
import requests

# Optional ADK client (preferred if available in your ADK version)
try:
    from adk import AgentClient
    _HAS_AGENT_CLIENT = True
except Exception:
    _HAS_AGENT_CLIENT = False


class DataScoutAgent(Agent):
    """
    Extracts structured incidents from transcripts/news using Gemini and dispatches
    to the ResourcePlanner agent for NGO matching.
    """

    def __init__(self):
        super().__init__(name="datascout-adk")
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        init(project=project, location=location)

        self.model = GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
        self.db = firestore.Client(database=os.getenv("GOOGLE_CLOUD_FIRESTORE_DB"))

        # Inter-agent config
        self.planner_agent_name = os.getenv("RESOURCE_PLANNER_AGENT_NAME", "resourceplanner-adk")
        self.planner_http_url = os.getenv("RESOURCE_PLANNER_URL")  # e.g., https://<run-url>/actions/plan_matches

        # Prepare optional ADK client
        self._planner_client: Optional["AgentClient"] = None
        if _HAS_AGENT_CLIENT:
            try:
                self._planner_client = AgentClient(self.planner_agent_name)
            except Exception:
                self._planner_client = None

    # ---------- capabilities ----------

    @action()
    def summarize_text(self, text: str) -> Dict[str, Any]:
        """
        Convert raw disaster text to a compact incident JSON:
        {location, disaster_type, summary, needs: [str]}
        """
        prompt = f"""
Read this disaster update and output compact JSON with keys:
location, disaster_type, summary, needs (array of strings).
Only return valid JSON. No markdown fences.
Text: {text}
"""
        resp = self.model.generate_content(prompt)
        content = (resp.text or "").strip()
        # Be defensive: strip accidental fences
        if content.startswith("```"):
            content = content.strip("` \n")
            # In case someone wrapped with json
            if content.startswith("json"):
                content = content[4:].strip()

        try:
            obj = json.loads(content)
        except Exception:
            obj = {"location": "unknown", "disaster_type": "unknown", "summary": content, "needs": []}
        # Normalize types
        obj["needs"] = obj.get("needs", []) or []
        if not isinstance(obj["needs"], list):
            obj["needs"] = [str(obj["needs"])]
        return obj

    @action()
    def ingest_from_transcripts(self, limit: int = 20) -> Dict[str, Any]:
        """
        Read latest 'transcripts' documents and create incidents; dispatch each to planner.
        """
        docs = (
            self.db.collection("transcripts")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        created, dispatched = 0, 0
        for d in docs:
            text = d.to_dict().get("text", "")
            if not text:
                continue
            inc = self.summarize_text(text)
            _, ref = self._create_incident(inc)
            created += 1
            if self._dispatch_to_planner(inc, incident_id=ref.id):
                dispatched += 1

        return {"created": created, "dispatched": dispatched}

    @action()
    def ingest_from_feed(self, items: List[str]) -> Dict[str, Any]:
        """
        Ingest already-fetched RSS/news items (array of strings). Create incidents and dispatch.
        """
        created, dispatched = 0, 0
        for raw in items:
            inc = self.summarize_text(raw)
            _, ref = self._create_incident(inc)
            created += 1
            if self._dispatch_to_planner(inc, incident_id=ref.id):
                dispatched += 1
        return {"created": created, "dispatched": dispatched}
    
    @action()
    def fetch_and_ingest(self):
        """
        Automatically fetch top disaster RSS/news items and process them.
        """
        urls = [
            "https://www.reliefweb.int/rss/updates.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml"
        ]
        items = []
        for u in urls:
            feed = feedparser.parse(u)
            for e in feed.entries[:10]:
                items.append(e.title + " " + e.summary)
        return self.ingest_from_feed(items=items)
    

    @action()
    def update_ngos_from_reliefweb(self, limit: int = 200) -> Dict[str, Any]:
        """
        Pulls factual NGO data from ReliefWeb API and updates Firestore 'ngos' collection.
        Only stores key fields: name, service (if available), country.
        """

        url = f"https://api.reliefweb.int/v1/sources?appname=crisisconnect&profile=list&limit={limit}"
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return {"error": f"ReliefWeb API returned {resp.status_code}"}

        data = resp.json()
        docs = data.get("data", [])

        added = 0
        for d in docs:
            f = d.get("fields", {})
            name = f.get("name")
            country = (f.get("country") or {}).get("name", "Unknown")
            if not name:
                continue

            # simple heuristic: infer service from NGO type keywords
            org_type = (f.get("type") or "").lower()
            if "medical" in org_type or "health" in org_type:
                service = "medical supplies"
            elif "food" in org_type or "hunger" in org_type:
                service = "food"
            elif "shelter" in org_type or "housing" in org_type:
                service = "shelter"
            else:
                service = "general aid"

            doc_id = name.lower().replace(" ", "_")
            self.db.collection("ngos").document(doc_id).set({
                "name": name,
                "service": service,
                "country": country,
                "source": "reliefweb",
            })
            added += 1

        return {"status": "updated", "count": added, "collection": "ngos"}



    # ---------- helpers ----------

    def _create_incident(self, inc: Dict[str, Any]):
        # Add server-side timestamp to help downstream ordering
        payload = {
            **inc,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        ref = self.db.collection("incidents").add(payload)[1]
        return payload, ref

    def _dispatch_to_planner(self, inc: Dict[str, Any], incident_id: Optional[str] = None) -> bool:
        """
        Preferred: use ADK AgentClient.
        Fallback: HTTP POST to planner Cloud Run URL at /actions/plan_matches
        """
        req = {"incident": inc, "incident_id": incident_id}

        # 1) ADK client if available and resolved
        if self._planner_client is not None:
            try:
                _ = self._planner_client.call("plan_matches", req)
                return True
            except Exception:
                pass

        # 2) HTTP fallback if URL provided
        if self.planner_http_url:
            try:
                # Planner ADK action endpoint: POST /actions/<action_name>
                url = self.planner_http_url.rstrip("/")
                if not url.endswith("/actions/plan_matches"):
                    url = f"{url}/actions/plan_matches"
                r = requests.post(url, json=req, timeout=10)
                return r.status_code // 100 == 2
            except Exception:
                return False

        return False


root_agent = DataScoutAgent()
