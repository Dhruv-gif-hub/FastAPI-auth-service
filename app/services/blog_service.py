from ..repositories.blog_repository import BlogContentRepository
from ..repositories.comment_repository import CommentRepository
from fastapi import Depends 
from ..dependencies.db import get_blog_repo, get_comment_repo, get_redis
from ..models.post import Blog_model, Blog_update
import json

class BlogService:

    def __init__(self, blog_repo: BlogContentRepository = Depends(get_blog_repo), 
                 comment_repo: CommentRepository = Depends(get_comment_repo), 
                 redis = Depends(get_redis)):
        self.blog_repo = blog_repo
        self.comment_repo = comment_repo
        self.redis = redis

    async def get_blog(self,blog_id: str):
        cached = await self.redis.get(f"blog:{blog_id}")
        if cached:
            return json.loads(cached)
        blog = await self.blog_repo.create_blog_response(blog_id)

        await self.redis.set(
        f"blog:{blog_id}",
        blog.model_dump_json(),
        ex=3600 
        )

        return blog
    
    async def create_blog(self, blog: Blog_model):
        return await self.blog_repo.create(blog)
    
    async def get_blogs_by_author(self, author_id: str):
        cached = await self.redis.get(f"author_blogs:{author_id}")
        if cached:
            return json.loads(cached)
        blogs = await self.blog_repo.get_by_author_id(author_id)
        blogs_json = json.dumps([blog.model_dump() for blog in blogs])
        await self.redis.set(
            f"author_blogs:{author_id}",
            blogs_json,
            ex=3600
        )
        return blogs
    
    async def update_blog(self, blog_id: str, updates: Blog_update):
        await self.blog_repo.update_blog(blog_id, updates)
        await self.redis.delete(f"blog:{blog_id}")
        return (f'Blog with id {blog_id} updated successfully')
    
    async def get_all_blogs(self):
        return await self.blog_repo.get_all_blogs()
    
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
        comments_json = json.dumps([comment.model_dump() for comment in comments])
        await self.redis.set(
            f"blog_comments_by_id:{comment_id}",
            comments_json,
            ex=3600
        )
        return comments
    
    async def delete_comment(self, comment_id):
        await self.comment_repo.delete_comment(comment_id)
        await self.redis.delete(f"blog_comments_by_id:{comment_id}")
        return (f'Comment with id {comment_id} deleted successfully')
    
    async def update_comment(self, comment_id, new_content):
        await self.comment_repo.update_comment(comment_id, new_content)
        await self.redis.delete(f"blog_comments_by_id:{comment_id}")
        return (f'Comment with id {comment_id} updated successfully')
    