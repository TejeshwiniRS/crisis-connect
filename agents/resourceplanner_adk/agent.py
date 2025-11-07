from typing import Dict, Any, List
from google.cloud import firestore

class ResourcePlannerAgent:
    def __init__(self):
        self.db = firestore.Client(database="crisisconnect")

    def _find_ngos_for_need(self, need: str) -> List[Dict[str, str]]:
        # Minimal Firestore query; seed "ngos" collection beforehand.
        docs = self.db.collection("ngos").where("service", "==", need).stream()
        return [d.to_dict() for d in docs]

    def plan(self) -> Dict[str, Any]:
        # Iterate incidents without matches (simple demo filter)
        incs = list(self.db.collection("incidents").limit(50).stream())
        matched = 0
        for inc in incs:
            data = inc.to_dict()
            needs = data.get("needs", [])
            matches: List[Dict[str, str]] = []
            for n in needs:
                matches.extend(self._find_ngos_for_need(n))
            if matches:
                self.db.collection("matches").document(inc.id).set({"incident": data, "matches": matches})
                matched += 1
        return {"matched_incidents": matched}

root_agent = ResourcePlannerAgent()
