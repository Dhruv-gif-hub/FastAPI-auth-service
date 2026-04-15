from fastapi import APIRouter, Depends, status, HTTPException
from typing_extensions import Annotated
from ..dependencies.Scope import require_read_user, require_write_user
from ..models.user import UserInDB, Update_user
from ..dependencies.db import get_db
from ..repositories.database import Database
from ..models.post import post
from ..core.security import get_password_hash
from ..core.utils import verify_password
from typing import Dict
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users")

@router.get("/me", response_model=Dict[str, post])
def profile_access(user : Annotated[UserInDB, Depends(require_read_user)]):
    return user

    
@router.post("/me", status_code=status.HTTP_202_ACCEPTED)
def post_creation(db : Annotated[Database , Depends(get_db)] , 
                  user : Annotated[UserInDB, Depends(require_write_user)],
                  data: post):
    data_db = {
        "Title": data.Title,
        "Content": data.Content
    }
    db.posting(user.username, data_db)
    return {
        "Message": "Posted"
    }

@router.get("/posts")
def posts(db: Annotated[Database, Depends(get_db)],
          user: Annotated[UserInDB, Depends(require_read_user)]):
    data = db.post_access(user.username)
    return JSONResponse(content=data, status_code=200)


@router.patch("/update_me")
def update_profile(db: Annotated[Database, Depends(get_db)],
                   user: Annotated[UserInDB, Depends(require_write_user)],
                   data: Update_user):
    if data.username is not None:
        db.update(user.username, "username", data.username)

    if data.email is not None:
        db.update(user.username, "email", data.email)

    return {
        "Message": "Updated"
    }

@router.post(("/me/change-password"))
def update_password(db: Annotated[Database, Depends(get_db)],
                    user: Annotated[UserInDB, Depends(require_write_user)],
                    current_password: str,
                    new_password: str):
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    hash_password = get_password_hash(new_password)
    db.update(user.username, "hashed_password" , hash_password)
    return {
        "Message": "Updated"
    }




