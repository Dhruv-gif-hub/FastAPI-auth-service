from ..database.mongo import BlogContent
from ..models.post import Blog_model
from ..database.postgres import Blog
from ..dependencies.db import get_db
from fastapi import Depends

class BlogContentRepository:

    async def create(self, blog: Blog_model, db = Depends(get_db)):

        content_blog = BlogContent(

            blog_id = blog.mongo_content_id,
            content = blog.Content

        )
        blog_postgres = Blog(

            author_id = blog.author_id,
            mongo_content_id = blog.mongo_content_id,
            title = blog.Title,
            status = blog.status

        )
        db.add(blog_postgres)
        return await content_blog.insert()
    
    async def get_by_blog_id(self,blog_id: str):
        return await BlogContent.find_one(
            BlogContent.blog_id == blog_id
        )
