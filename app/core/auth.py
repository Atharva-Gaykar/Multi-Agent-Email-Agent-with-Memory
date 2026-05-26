from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib
import base64
from app.core.config import settings
from app.database.connection import get_session
from app.database.models import User


# CONFIG


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# auto_error=False → allows us to return 401 instead of FastAPI's 403
security = HTTPBearer(auto_error=False)


# TOKEN LOGIC


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with UTC-aware expiration
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "sub": str(data.get("id"))  # JWT best practice
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token and return payload
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# CURRENT USER DEPENDENCY


async def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
) -> User:
    """
    Fetch the logged-in user from DB using JWT payload
    """
    user_id = token_data.get("id")

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

# PASSWORD LOGIC (bcrypt-safe, unlimited length)
