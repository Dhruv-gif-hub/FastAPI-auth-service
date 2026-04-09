from fastapi import Depends, HTTPException, status
from datetime import timedelta
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..core.config import config
from ..core.security import get_user, verify_password, create_access_token, password_hash
from ..models.auth_model import Token
from ..repositories.database import fake_db

hash_value = password_hash.hash(config.HASH_KEY)

def authenticate_user(fake_db, username: str, password: str):

    user = get_user(fake_db, username)
    if not user:
        verify_password(password, hash_value)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def login_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
        ):
    user = authenticate_user(fake_db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    acces_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=acces_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")