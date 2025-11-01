import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.routes import auth, incidents, chats, health

app = FastAPI(title="CrisisConnect API", version="1.0")

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
app.include_router(chats.router, prefix="/api/v1/chats", tags=["chats"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
