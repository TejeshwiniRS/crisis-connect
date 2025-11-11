from typing import Dict, Any, List, Optional
import os
from google.cloud import firestore
from adk import Agent, action


class ResourcePlannerAgent(Agent):
    """
    Matches incidents' needs to NGOs by service in Firestore.
    """

    def __init__(self):
        super().__init__(name="resourceplanner-adk")
        self.db = firestore.Client(database=os.getenv("GOOGLE_CLOUD_FIRESTORE_DB"))

    # ---------- capabilities ----------

    @action()
    def plan_matches(self, incident: Dict[str, Any], incident_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Given a single incident JSON, find matching NGOs and persist a match document.
        Input: { incident: {...}, incident_id?: "abc123" }
        """
        needs = incident.get("needs", []) or []
        if not isinstance(needs, list):
            needs = [str(needs)]

        matches: List[Dict[str, Any]] = []
        for need in needs:
            matches.extend(
                self._find_ngos_for_need(
                    str(need).strip().lower(),
                    incident.get("country")
                )
            )

        if matches:
            match_doc = {
                "incident_id": incident_id,
                "incident": incident,
                "matches": matches,
                "created_at": firestore.SERVER_TIMESTAMP,
            }
            # Use incident_id if provided for idempotency
            if incident_id:
                self.db.collection("matches").document(incident_id).set(match_doc)
            else:
                self.db.collection("matches").add(match_doc)

        return {"need_count": len(needs), "match_count": len(matches)}

    @action()
    def plan_unmatched_incidents(self, limit: int = 50) -> Dict[str, Any]:
        """
        Sweep mode: look at recent incidents and create matches for those
        that don't have a corresponding entry in 'matches'.
        """
        incs = list(self.db.collection("incidents").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream())
        processed, matched = 0, 0
        for inc in incs:
            incident_id = inc.id
            is_matched = self.db.collection("matches").document(incident_id).get().exists
            if is_matched:
                continue

            data = inc.to_dict() or {}
            res = self.plan_matches(incident=data, incident_id=incident_id)
            processed += 1
            if res.get("match_count", 0) > 0:
                matched += 1

        return {"processed": processed, "newly_matched_incidents": matched}

    # ---------- helpers ----------

    def _find_ngos_for_need(self, need: str, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Finds NGOs that offer a given service (need).
        Preference order:
          1. Same country
          2. Global fallback if none found
        """
        need = (need or "").strip().lower()
        if not need:
            return []

        q = self.db.collection("ngos").where("service", "==", need).stream()
        all_ngos = [d.to_dict() for d in q]
        if not all_ngos:
            return []

        if country:
            country = country.strip().lower()
            same_country = [
                n for n in all_ngos if n.get("country", "").lower() == country
            ]
            if same_country:
                return same_country

        # fallback: return all NGOs for this service
        return all_ngos



root_agent = ResourcePlannerAgent()
