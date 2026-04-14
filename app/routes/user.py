from fastapi import APIRouter, Depends
from typing_extensions import Annotated
from ..dependencies.Scope import require_read_user, require_write_user
from ..routes.user import UserInDB
from ..dependencies.db import get_db
from ..repositories.database import Database
from typing import List

router = APIRouter(prefix="/users")

@router.get("/me")
def profile_access(user : Annotated[UserInDB, Depends(require_read_user)]):
    return user.posts

    