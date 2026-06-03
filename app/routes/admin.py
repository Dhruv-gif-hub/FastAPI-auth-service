from fastapi import APIRouter, Depends, Query, Path, Body
from ..dependencies.db import get_db
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies.Scope import require_admin
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService
from uuid import UUID
from ..services.comment_service import CommentService
from ..services.blog_service import BlogService

router = APIRouter(prefix="/admin")

@router.get("/users")
def users(last_id: Annotated[UUID, Body()],
          user_in_db : Annotated[UserService, Depends(UserService)],
          user_repo : Annotated[UserRepository, Depends(UserRepository)],
          user = Depends(require_admin),
          page_size: Annotated[int | None, Query()] = None
          ):
    return user_in_db.get_all_users(user,user_repo, last_id, page_size)
    

@router.get("/users/{username}")
def find_user(user_in_db : Annotated[UserService, Depends(UserService)],
              user_repo : Annotated[UserRepository, Depends(UserRepository)],
              username: Annotated[str, Path(title="The name of the user to get")],
              user = Depends(require_admin)
              ):
    return user_in_db.get_user(user_repo, username,user)

@router.patch("/users/{username}/role")
def create_admin(user_in_db : Annotated[UserService, Depends(UserService)],
                 user_repo : Annotated[UserRepository, Depends(UserRepository)],
                 username: Annotated[str, Path(title="The name of the user to get")],
                 db : Annotated[AsyncSession, Depends(get_db)],
                 user = Depends(require_admin)
                 ):
    update_user =  user_in_db.get_user(user_repo, username,user)
    if update_user:
        update_user.role = "admin"
        db.add(update_user)

@router.delete("/hard_delete/{user_id}")
def hard_delete(user_in_db : Annotated[UserService, Depends(UserService)],
                        user_id : Annotated[UUID, Path(title="The id of the user to get")],
                        user = Depends(require_admin)
                        ):
    if not user:
        return None
    result = user_in_db.deleting_user(user_id)
    return {
        "Message": "Deactivated"
    }

@router.delete("/soft_delete/{user_id}")
def deleting_account(user_in_db : Annotated[UserService, Depends(UserService)],
                     user_id : Annotated[UUID, Path(title="The id of the user to get")],
                     user = Depends(require_admin)
                     ):
    if not user:
        return None
    return user_in_db.soft_delete(user_id)


@router.delete("/comment/{comment_id}")
def soft_delete(comment_id : Annotated[str, Path()],
                      user_in_db : Annotated[UserService, Depends(UserService)],
                      service : Annotated[CommentService, Depends(CommentService)],
                      user = Depends(require_admin)):
    if user:
        return service.delete_comment(comment_id, user_in_db)

@router.delete("/hard_delete_comment/{comment_id}")
def hard_delete_comment(comment_id : Annotated[str, Path()],
                        service : Annotated[CommentService, Depends(CommentService)],
                        user = Depends(require_admin)
                        ):
    if user:
        return service.hard_delete(comment_id)
    

@router.delete("/blog,{blog_id}")
def hard_delete_blog(post : Annotated[BlogService, Depends(BlogService)],
                blog_id : Annotated[str, Path()],
                user = Depends(require_admin)
                ):
    return post.hard_delete(blog_id)

