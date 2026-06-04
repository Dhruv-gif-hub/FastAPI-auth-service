from ..repositories.blog_repository import BlogContentRepository
from ..repositories.comment_repository import CommentRepository
from ..repositories.user_repository import UserRepository
from ..caching.redis import redis_client # Your global client instance
from fastapi import Depends
from ..dependencies.db import get_db

# These functions act as factories
async def get_blog_repo():
    return BlogContentRepository(session=Depends(get_db))

async def get_comment_repo():
    return CommentRepository()

async def get_redis():
    return redis_client    

async def get_user_repo():
    return UserRepository()
