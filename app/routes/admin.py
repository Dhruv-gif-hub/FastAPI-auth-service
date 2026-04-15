from fastapi import APIRouter, Depends, Query, Path, HTTPException
from ..dependencies.db import get_db
from typing_extensions import Annotated
from ..repositories.database import Database
from ..dependencies.Scope import require_admin
from ..models.user import UserInDB

router = APIRouter(prefix="/admin")

@router.get("/users")
def users(limit: Annotated[int, Query(le=11)],
          db : Annotated[Database , Depends(get_db)],
          user : Annotated[UserInDB, Depends(require_admin)],
          cursor: Annotated[str | None, Query()] = None
          ):
    users = list(db.file.items())
    users.sort(key=lambda x: x[0])
    start_index = 0

    if cursor:
        for i, (username, _) in enumerate(users):
            if username == cursor:
                start_index = i + 1
                break
    
    paginated_users = users[start_index:start_index + limit]
    result = [data for _, data in paginated_users]
    next_cursor = None
    if len(paginated_users) == limit:
        next_cursor = paginated_users[-1][0]

    return {
        "data": result,
        "next_cursor": next_cursor
    }

@router.get("/users/{username}")
def find_user(db : Annotated[Database , Depends(get_db)],
              user : Annotated[UserInDB, Depends(require_admin)],
              username: Annotated[str, Path(title="The name of the user to get")]
              ):
    return db.get_user(username)

@router.patch("/users/{username}/role")
def create_admin(db : Annotated[Database , Depends(get_db)],
                 user : Annotated[UserInDB, Depends(require_admin)],
                 username: Annotated[str, Path(title="The name of the user to get")]
                 ):
    if username not in db.file:
        raise HTTPException(
            status_code=404,
            detail="User does not exit"
        )
    db.admin_role(username)
    return {
        "Message": "Created"
    }

@router.delete("/users/{username}")
def deactivate_account(db : Annotated[Database , Depends(get_db)],
                 user : Annotated[UserInDB, Depends(require_admin)],
                 username: Annotated[str, Path(title="The name of the user to get")]
                 ):
    if username not in db.file:
        raise HTTPException(
            status_code=404,
            detail="User does not exit"
        )
    db.deactivating_account(username)
    return {
        "Message": "Deactivated"
    }

@router.delete("/users/{username}")
def hard_delete(db : Annotated[Database , Depends(get_db)],
                user : Annotated[UserInDB, Depends(require_admin)],
                username: Annotated[str, Path(title="The name of the user to get")]
                ):
    if username not in db.file:
        raise HTTPException(
            status_code=404,
            detail="User does not exit"
        )
    db.delete_data(username)
    return {
        "Message": "User_deleted"
    }
    
