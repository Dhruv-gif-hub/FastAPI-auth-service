from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordBearer,SecurityScopes
import jwt
from .config import config
from ..models.auth_model import TokenData
from ..dependencies.db import get_db
from ..repositories.database import Database
from ..core.utils import password_hash, blacklisted_tokens

    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token" ,
                                     scopes={
                                         "read:user":"Read User Info",
                                         "write:user":"Modify User Info",
                                         "delete:user":"Delete User"
                                     })
        
def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy() # to avoid mutating the original data
    if expires_delta:

        expire = datetime.now(timezone.utc) + expires_delta

    else:

        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    
    return encoded_jwt

def get_current_user(security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)], 
        request: Request,
        db : Annotated[Database, Depends(get_db)]):
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value}
        )
    if token in blacklisted_tokens:
        return None
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        scope_str = payload.get("scope", "")
        token_scopes = scope_str.split(" ")

        token_data = TokenData(username=username,scopes=token_scopes)

    except jwt.InvalidTokenError:
        raise credentials_exception
    user = db.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for required_scope in security_scopes.scopes:
        if required_scope not in token_data.scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user
