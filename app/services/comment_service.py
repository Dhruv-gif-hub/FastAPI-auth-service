from ..repositories.comment_repository import CommentRepository
from fastapi import Depends 
from ..dependencies.service_dependencies import get_comment_repo, get_redis
import json

class CommentService:

    def __init__(self, comment_repo: CommentRepository = Depends(get_comment_repo), 
                 redis = Depends(get_redis)):
        self.comment_repo = comment_repo
        self.redis = redis

    async def get_comments_for_blog(self, blog_id: str):
        cached = await self.redis.get(f"blog_comments:{blog_id}")
        if cached:
            return json.loads(cached)
        comments = await self.comment_repo.get_blog_comments(blog_id)
        comments_json = json.dumps([comment.model_dump() for comment in comments])
        await self.redis.set(
            f"blog_comments:{blog_id}",
            comments_json,
            ex=3600
        )
        return comments
    
    async def add_comments(self, comment_model):
        return await self.comment_repo.create(comment_model)
    
    async def get_comment_by_id(self, comment_id: str):
        cached = await self.redis.get(f"blog_comments_by_id:{comment_id}")
        if cached:
            return json.loads(cached)
        comments = await self.comment_repo.get_comment_by_id(comment_id)
        comments_json = json.dumps(comments)
        await self.redis.set(
            f"blog_comments_by_id:{comment_id}",
            comments_json,
            ex=3600
        )
        return comments
    
    async def delete_comment(self, comment_id, user_in_db):
        user = user_in_db.profile_access()
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            return None
        if comment.user_id != user.id and user.role == "user":
            return None
        await self.comment_repo.delete_comment(comment_id)
        await self.redis.delete(f"blog_comments_by_id:{comment_id}")
        return (f'Comment with id {comment_id} deleted successfully')
    
    async def update_comment(self, comment_id, new_content, user_in_db):
        user = user_in_db.profile_access()
        comment = await self.get_comment_by_id(comment_id)
        if not comment:
            return None
        if comment.user_id != user.id:
            return None
        await self.comment_repo.update_comment(comment_id, new_content)
        await self.redis.delete(f"blog_comments_by_id:{comment_id}")
        return (f'Comment with id {comment_id} updated successfully')
    
    async def hard_delete(self, comment_id):
        await self.redis.delete(f"blog_comments_by_id:{comment_id}")
        return self.comment_repo.hard_delete_comment(comment_id)