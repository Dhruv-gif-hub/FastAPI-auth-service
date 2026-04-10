from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash
from .config import config
from ..models.auth_model import TokenData
from ..repositories.database import fake_db

    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy() # to avoid mutating the original data
    if expires_delta:

        expire = datetime.now(timezone.utc) + expires_delta

    else:

        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = fake_db.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
