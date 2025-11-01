import bcrypt

from datetime import datetime, timedelta, timezone
from jose import jwt

from app.config import settings

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=4)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expires_delta})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def verify_password(plain_password, hashed_password):
    plain_password = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(plain_password, hashed_password.encode("utf-8"))

def get_password_hash(password: str) -> str:
    password = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode("utf-8")
