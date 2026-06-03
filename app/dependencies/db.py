from ..database.postgres import Session_local
from ..repositories.blog_repository import BlogContentRepository
from ..repositories.comment_repository import CommentRepository
from ..repositories.user_repository import UserRepository
from ..caching.redis import redis_client # Your global client instance
from fastapi import Depends

async def get_db():
    async with Session_local() as session:
        try:
            yield session
            await session.commit() 
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# These functions act as factories
async def get_blog_repo():
    return BlogContentRepository(session=Depends(get_db))

async def get_comment_repo():
    return CommentRepository()

async def get_redis():
    return redis_client    

async def get_user_repo():
    return UserRepository()
