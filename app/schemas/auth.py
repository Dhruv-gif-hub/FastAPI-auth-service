from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from datetime import timedelta
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from ..core.config import config
from ..core.security import verify_password, create_access_token, password_hash, create_refresh_token, oauth2_scheme
from ..models.auth_model import Token
from ..repositories.database import fake_db
from ..models.user import signupUser
from ..dependencies.rate_limiter import rate_limiter
from ..services.exceptions import credentials_exception
import jwt
from ..models.auth_model import TokenData
from ..core.roles import ROLE_SCOPE_MAP

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
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        response: Response 
        ):
    user = authenticate_user(fake_db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password"
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
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=1800,  # 30 min
            samesite="lax"
        )
    
    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7*24*60*60,  # 7 days
            samesite="lax"
        )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/signup", tags=["Sign_Up"], dependencies=[Depends(signup_limiter)])
def signup_access_token(data: signupUser):
    user = signup_user(fake_db, data.username ,data.password)

    return {
        "message": "User created successfully",
        "username": user["username"]
    }

blacklisted_tokens = set()

@router.post("/logout")
def logout(response: Response, token: str = Depends(oauth2_scheme)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    blacklisted_tokens.add(token)
    return {"message": "Logged out"}

@router.post("/refresh")
def refresh_token(refresh_token : Annotated[str|None,Cookie()], response: Response):
    # Alternate
    # refresh_token = request.cookies.get("access_token") where request:Request 
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
    
    user = fake_db.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    user_scopes = ROLE_SCOPE_MAP.get(user.role, [])
    acces_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
            data={"sub": user.username,
                  "scope":" ".join(user_scopes)}, expires_delta=acces_token_expires
        )
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=900,
        samesite="lax"
    )

    return {"message": "Access token refreshed"}