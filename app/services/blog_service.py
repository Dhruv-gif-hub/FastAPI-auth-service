from ..repositories.blog_repository import BlogContentRepository
from ..repositories.comment_repository import CommentRepository
from ..caching.redis import redis_client
from ..database.mongo import ContentBlock
class BlogService:

    def __init__(
        self,
        BlogContentRepository,
        CommentRepository,
        redis_client
    ):
        self.blog_repo = BlogContentRepository
        self.comment_repo = CommentRepository
        self.redis = redis_client

    async def get_blog(
    self,
    blog_id: str
):
        
        cached = await self.redis.get(f"blog:{blog_id}")
        if cached:
            return cached
        blog = await self.blog_repo.get_by_blog_id(blog_id)

        await self.redis.set(
        f"blog:{blog_id}",
        blog.model_dump_json(),
        ex=3600
        )

        return blog
    
    async def create_blog(
            self,
            blog_id: str,
            content: ContentBlock
    ):
        