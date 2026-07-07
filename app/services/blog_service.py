from ..repositories.blog_repository import BlogContentRepository
from fastapi import Depends 
from asyncio import gather
from ..dependencies.service_dependencies import get_blog_repo, get_redis
from ..models.post import Blog_model, Blog_update
import json

# This act as a layer between the user and the database.
# From here the user's requests are mapped with the relevant database query function.
# This lists all the functionalities related to the blogs.
class BlogService:

    def __init__(self, blog_repo: BlogContentRepository = Depends(get_blog_repo), 
                redis = Depends(get_redis)):
        self.blog_repo = blog_repo
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
    
    async def get_blogs_by_author(self, author_id):
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
    
    async def update_blog(self, blog_id: str, user_in_db, updates: Blog_update):
        user = user_in_db.profile_access()
        result = await self.blog_repo.update_blog(user, blog_id, updates)
        if not result:
            return None
        await self.redis.delete(f"blog:{blog_id}")
        return (f'Blog with id {blog_id} updated successfully')
    
    async def delete_blog(self, blog_id: str):
        await gather(
            self.blog_repo.delete_blog(blog_id),
            self.redis.delete(f"blog:{blog_id}")
        )
        return (f"Blog with id {blog_id} soft deleted successfully")
        
    async def get_all_blogs(self,last_id, page_size):
        return await self.blog_repo.get_all_blogs(last_id, page_size)
    
    async def hard_delete(self, blog_id:str):
        await gather(
            self.blog_repo.hard_delete(blog_id),
            self.redis.delete(f"blog:{blog_id}")
        )
        return (f"Blog with id {blog_id} deleted successfully")