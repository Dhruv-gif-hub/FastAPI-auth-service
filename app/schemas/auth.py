from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..core.config import config
from ..core.security import verify_password, create_access_token, password_hash
from ..models.auth_model import Token
from ..repositories.database import fake_db
from ..models.user import signupUser
from ..dependencies.rate_limiter import rate_limiter


router = APIRouter(prefix="/auth")

login_limiter = rate_limiter(limit=5, window_seconds=60)
signup_limiter = rate_limiter(limit=3, window_seconds=60)

hash_value = password_hash.hash(config.HASH_KEY)

def authenticate_user(fake_db, username: str, password: str):

    user = fake_db.get_user(username)
    if not user:
        verify_password(password, hash_value)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def signup_user(fake_db, username: str, password: str):
    if username in fake_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_password = password_hash.hash(password)

    user_data = {
        "username": username,
        "hashed_password": hashed_password
    }

    fake_db[username] = user_data

    return user_data

@router.post("/token", response_model=Token, dependencies=[Depends(login_limiter)])
def login_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
        ):
    user = authenticate_user(fake_db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password"
            )
    acces_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=acces_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/signup", tags=["Sign_Up"], dependencies=[Depends(signup_limiter)])
def signup_access_token(data: signupUser):
    user = signup_user(fake_db, data.username ,data.password)

    return {
        "message": "User created successfully",
        "username": user["username"]
    }