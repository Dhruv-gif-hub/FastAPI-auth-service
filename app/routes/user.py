from fastapi import APIRouter, Depends, status, Body, Path, HTTPException, Query
from ..models.user import Update_user
from ..models.post import Blog_model, Blog_update, Comment_model
from ..repositories.user_repository import UserRepository
from ..services.blog_service import BlogService
from ..services.user_service import UserService
from ..services.comment_service import CommentService
from typing import Annotated
from ..dependencies.Scope import require_read_user

# This file contains the routes related to user profile access, post creation, and profile updates.
router = APIRouter(prefix="/users")

@router.get("/me")
def profile(user_in_db : Annotated[UserService, Depends(UserService)],
            user_check = Depends(require_read_user)):
    return user_in_db.profile_access(user_check)

    
@router.post("/me", status_code=status.HTTP_202_ACCEPTED)
def post_creation(user_in_db : Annotated[UserService, Depends(UserService)],
                  data : Annotated[Blog_model, Body()],
                  post : Annotated[BlogService, Depends(BlogService)],
                  user_check = Depends(require_read_user)):
    user = user_in_db.profile_access(user_check)
    if data.author_id == user.id:
        result = post.create_blog(data)
        return {
            "Message": "Posted"
        }

@router.get("/vector_search")
def blog_vector(search_text : Annotated[str, Body()],
                user_in_db : Annotated[UserService, Depends(UserService)]):
    return user_in_db.blog_vector(search_text)

@router.get("/posts")
def posts(user_in_db : Annotated[UserService, Depends(UserService)],
          post : Annotated[BlogService, Depends(BlogService)],
          user_check = Depends(require_read_user)):
    user = user_in_db.profile_access(user_check)
    values = post.get_blogs_by_author(user.id)
    return values

@router.get("/post_id/{blog_id}/retrieval")
def post_by_id(post : Annotated[BlogService, Depends(BlogService)],
               blog_id = Path(title="Blog_id of the blog to find")):
    return post.get_blog(blog_id)

@router.patch("update_blog")
def update_post(user_in_db : Annotated[UserService, Depends(UserService)],
                blog_id : Annotated[str, Body()], 
                blog: Annotated[Blog_update, Body()],
                post : Annotated[BlogService, Depends(BlogService)]):
    result = post.update_blog(blog_id, user_in_db, blog)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this blog"
        )
    
@router.get("/blog_feed")
def get_all(post : Annotated[BlogService, Depends(BlogService)],
            last_id : Annotated[str|None, Query()] = None,
            page_size : Annotated[int|None, Query()] = None):
    result = post.get_all_blogs(last_id, page_size)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )

@router.patch("/update_me")
def update_profile(data : Annotated[Update_user, Body()],
                   user_repo : Annotated[UserRepository, Depends(UserRepository)],
                   user_in_db : Annotated[UserService, Depends(UserService)],
                   user_check = Depends(require_read_user)):
    user = user_in_db.profile_access(user_check)
    return user_in_db.update_profile(user, data, user_repo)


@router.post(("/me/change-password"))
def update_password(user_repo : Annotated[UserRepository, Depends(UserRepository)],
                    user_in_db : Annotated[UserService, Depends(UserService)],
                    current_password: Annotated[str, Body(...)],
                    new_password: Annotated[str, Body(...)],
                    user_check = Depends(require_read_user)):
    user = user_in_db.profile_access(user_check)
    return user_in_db.update_password(user,user_repo, current_password, new_password)


@router.post("/comment")
def commenting(service : Annotated[CommentService, Depends(CommentService)],
               model : Annotated[Comment_model, Body()]):
    return service.add_comments(model)

@router.get("/comment/{blog_id}/retrieval")
def comment_through_blog(blog_id : Annotated[str, Path()],
                         service : Annotated[CommentService, Depends(CommentService)]):
    return service.get_comments_for_blog(blog_id)

@router.get("/comment/{comment_id}")
def get_comment_id(comment_id : Annotated[str, Path()],
                   service : Annotated[CommentService, Depends(CommentService)]):
    return service.get_comment_by_id(comment_id)

@router.delete("/comment/{comment_id}")
def delete_comment_id(comment_id : Annotated[str, Path()],
                      user_in_db : Annotated[UserService, Depends(UserService)],
                      service : Annotated[CommentService, Depends(CommentService)]):
    return service.delete_comment(comment_id, user_in_db)

@router.patch("comment/{comment_id}")
def update_comment(comment_id : Annotated[str, Path()],
                   content : Annotated[str, Body()],
                   user_in_db : Annotated[UserService, Depends(UserService)],
                    service : Annotated[CommentService, Depends(CommentService)]):
    return service.update_comment(comment_id, content, user_in_db)

@router.delete("/me")
def deleting_account(user_in_db : Annotated[UserService, Depends(UserService)],
                     user_check = Depends(require_read_user)):
    user = user_in_db.profile_access(user_check)
    return user.soft_delete(user.id)

@router.delete("/blog,{blog_id}")
def delete_blog(post : Annotated[BlogService, Depends(BlogService)],
                blog_id : Annotated[str, Path()],
                user = Depends(require_read_user)
                ):
    if user:
        return post.delete_blog(blog_id)
    return None