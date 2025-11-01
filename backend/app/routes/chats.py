from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_chats(request):
    """ Retrieve a list of existing chat sessions. """
    chats = []
    return {"status": "ok", "chats": chats}

@router.post("/")
async def create_chat(request):
    """ Create a new chat session. """
    chat = None
    return {"status": "ok", "chats": chat}

@router.get("/{chat_id}")
async def get_chat(chat_id):
    """ Retrieve a chat session. """
    chat = None
    return {"status": "ok", "chats": chat}

@router.post("/delete/{chat_id}")
async def delete_chat(chat_id):
    """ Delete a chat session. """
    return {"status": "ok"}

@router.post("/ask")
async def ask(request):
    """ Handle incoming question and enqueue it. """
    return {"job_id": "1234567890"}

# TODO: SSE endpoint