from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from datetime import timedelta
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..core.config import config
from ..core.security import create_access_token, create_refresh_token, oauth2_scheme
from ..models.auth_model import Token, TokenData
from ..models.user import signupUser
from ..dependencies.rate_limiter import rate_limiter
from ..services.exceptions import credentials_exception
import jwt
from ..core.roles import ROLE_SCOPE_MAP
from ..core.utils import verify_password, password_hash
from ..repositories.user_repository import UserRepository
from datetime import datetime, timedelta, timezone
from ..caching.redis import redis_client

router = APIRouter(prefix="/auth")

login_limiter = rate_limiter(max_requests=5, window_seconds=60)
signup_limiter = rate_limiter(max_requests=3, window_seconds=60)

hash_value = password_hash.hash(config.HASH_KEY)

def authenticate_user(db, username: str, password: str):

    user = db.get_by_username(username)

    if not user:
        verify_password(password, hash_value)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def signup_user(db, user):
    user_in_db = db.get_by_username(user.username)
    if not user_in_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    new_user = db.create_user(user)
    return new_user
    

@router.post("/token", response_model=Token, dependencies=[Depends(login_limiter)])
def login_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response,
        db = Depends(UserRepository)
        ):
    user = authenticate_user(db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password , or user is not active"
            )
    user_scopes = ROLE_SCOPE_MAP.get(user.role, [])
    acces_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username,
              "scope":" ".join(user_scopes)}, expires_delta=acces_token_expires
    )
    refresh_token_expires = timedelta(days=config.REFRESH_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    
    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60, # 7 days
            samesite="lax",
            secure=True
        )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", tags=["Sign_Up"], dependencies=[Depends(signup_limiter)])
def signup_access_token(data: signupUser, db = Depends(UserRepository)):
    user = signup_user(db, data)

    return {
        "message": "User created successfully",
        "username": user.username
    }


@router.post("/logout")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    response.delete_cookie("refresh_token")

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        exp_timestamp = payload["exp"]
        current_timestamp = datetime.now(timezone.utc)
        remaining_time = int(exp_timestamp - current_timestamp)
        if remaining_time > 0:
            redis_key = f"block_list:{token}"
            redis_client.set(redis_key, "logged_out", ex=remaining_time)
            return {"message": "Successfully logged out."}
        else:
            return {"message": "Token already expired, no need to blocklist."}
    
    except jwt.DecodeError:
        return {"error": "Invalid token format."}

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token : Annotated[str|None,Cookie()], db = Depends(UserRepository)):
    # Alternate
    # refresh_token = request.cookies.get("refresh_token") where request:Request 
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    try:
        payload = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = db.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    user_scopes = ROLE_SCOPE_MAP.get(user.role, [])
    acces_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
            data={"sub": user.username,
                  "scope":" ".join(user_scopes)}, expires_delta=acces_token_expires
        )

    return Token(access_token=new_access_token, token_type="bearer")