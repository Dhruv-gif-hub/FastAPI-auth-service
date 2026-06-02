from ..database.mongo import BlogContent
from ..models.post import Blog_model, Blog_update
from ..database.postgres import Blog
from sqlalchemy import select, and_
from beanie.operators import In
from ..models.response_models import BlogResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class BlogContentRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.db = session

    async def create(self, blog: Blog_model):

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
        self.db.add(blog_postgres)
        await content_blog.insert()
        return (f'Blog with id {blog.mongo_content_id} created successfully')
    
    async def get_by_blog_id(self, blog_id: str):
        stmt = select(Blog).where(and_(Blog.mongo_content_id == blog_id, Blog.is_active == True))
        result = await self.db.execute(stmt)
        blog = result.scalars().first()
        Content = await BlogContent.find_one(
            BlogContent.blog_id == blog_id
        )
        return [blog, Content]

    async def create_blog_response(self, blog_id: str, response_model = BlogResponse):
        values = await self.get_by_blog_id(blog_id)
        blog = values[0]
        Content = values[1]
        return BlogResponse(
            id = blog.mongo_content_id,
            author_id = blog.author_id,
            title = blog.title,
            status = blog.status,
            content = Content.content
        )
    
    async def get_by_author_id(self, author_id: str):
        stmt = select(Blog).where(and_(Blog.author_id == author_id, 
                                             Blog.is_active == True))
        result = await self.db.execute(stmt)
        blog = result.scalars().all()
        content_ids = [b.mongo_content_id for b in blog]
        if not content_ids:
            return []
        content = BlogContent.find(In(BlogContent.blog_id,content_ids))
        return await content.to_list()
    
    async def delete_blog(self, blog_id: str):
        values = await self.get_by_blog_id(blog_id)
        blog = values[0]
        Content = values[1]
        if blog:
            blog.is_active = False
            await self.db.commit()
        await Content.delete()
        return True
    
    async def update_blog(self, blog_id: str, updates: Blog_update):
        values = await self.get_by_blog_id(blog_id)
        blog = values[0]
        Content = values[1]
        if updates.Title:
            blog.title = updates.Title
        if updates.status:
            blog.status = updates.status
        if updates.Content:
            Content.content = updates.Content
            Content.updated_at = datetime.now()
            await Content.save()

    async def get_all_blogs(self, last_id: str|None = None, page_size: int = 10):
        if last_id:
            blogs = await BlogContent.find(BlogContent.blog_id < last_id).limit(page_size).to_list()
        else:
            blogs = await BlogContent.find().sort("blog_id").limit(page_size).to_list()

        next_last_id = None
        if blogs:
            next_last_id = (blogs[-1].blog_id)
        
        return blogs, next_last_id 
        