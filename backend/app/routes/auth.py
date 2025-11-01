from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.auth import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register")
async def register(request: dict, db: AsyncSession = Depends(get_db)):
    """ Register a new user. """
    email, name, password = request['email'], request['name'], request['password']
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = get_password_hash(password)
    user = User(
        email=email,
        name=name,
        hashed_password=hashed
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login(request: dict, db: AsyncSession = Depends(get_db)):
    """ Login and get JWT. """
    email, password = request['email'], request['password']
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
async def me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """ Decode JWT to identify current user. """
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=404, detail="User not found")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
