from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.config import settings
from app.utils.auth import create_access_token, verify_password, get_password_hash

users = {}

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register")
async def register(request: dict):
    """ Register a new user. """
    email, name, password = request['email'], request['name'], request['password']
    if email in users:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = get_password_hash(password)
    users[email] = {
        "name": name,
        "email": email,
        "hashed_password": hashed,
        "role": "user",
    }
    token = create_access_token({"sub": email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(request: dict):
    """ Login and get JWT. """
    email, password = request['email'], request['password']
    user = users.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)):
    """ Decode JWT to identify current user. """
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        email = payload.get("sub")
        if email not in users:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "email": email,
            "name": users[email]["name"],
            "role": users[email]["role"]
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
