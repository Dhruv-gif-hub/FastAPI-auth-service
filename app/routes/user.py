from fastapi import APIRouter, Depends, status, Body
from ..dependencies.Scope import require_read_user, require_write_user
from ..models.user import Update_user
from ..models.post import Blog_model
from ..repositories.user_repository import UserRepository
from ..services.blog_service import BlogService

# This file contains the routes related to user profile access, post creation, and profile updates.
router = APIRouter(prefix="/users")

@router.get("/me")
def profile_access(user = Depends(require_read_user)):
    return user

    
@router.post("/me", status_code=status.HTTP_202_ACCEPTED)
def post_creation(user = Depends(require_write_user),
                  data : Blog_model = Body(...),
                  post = Depends(BlogService)):
    if data.author_id == user.id:
        post.create_blog(data)
        return {
            "Message": "Posted"
        }

@router.get("/posts")
def posts(post = Depends(BlogService),
          user = Depends(require_read_user)):
    values = post.get_blogs_by_authour(user.id)
    return values


@router.patch("/update_me")
def update_profile(user = Depends(require_write_user),
                   data : Update_user = Body(...),
                   user_in_db = Depends(UserRepository)):
    user_in_db.updated_user_details(user.id, data)

    return {
        "Message": "Updated"
    }


@router.post(("/me/change-password"))
def update_password(user = Depends(require_write_user),
                    user_in_db = Depends(UserRepository),
                    current_password: str = Body(...),
                    new_password: str = Body(...)):
    user_in_db.update_password(user.id, current_password, new_password)
    return {
        "Message": "Updated"
    }




