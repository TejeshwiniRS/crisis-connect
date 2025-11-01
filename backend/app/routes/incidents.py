from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def create_incident(incident):
    """ Create a new incident. """
    return {"incident_id": "1234567890"}

@router.get("/{incident_id}")
async def get_incident(incident_id):
    """ Retrieve an incident. """
    return {"incident_id": incident_id}

@router.get("/")
async def list_incident(request):
    """ Retrieve all incidents."""
    incidents = []
    return {"incidents": []}