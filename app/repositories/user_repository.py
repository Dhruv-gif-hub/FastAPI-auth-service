from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from ..database.postgres import User, Blog
from ..models.user import signupUser, Update_user
from ..core.utils import get_password_hash
from ..core.utils import verify_password
from fastapi import HTTPException, Depends
from ..dependencies.db import get_db
from uuid import UUID

class UserRepository:

    def __init__(
        self,
        session: AsyncSession = Depends(get_db)
    ):
        self.session = session

    async def get_by_username(self, username: str):
        stmt = select(User).where(
            and_(User.username == username, User.is_active ==True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id):
        stmt = select(User).where(
            and_(User.id == user_id, User.is_active == True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, user: signupUser):
        hashed_password = get_password_hash(user.password)
        created_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email
        )
        self.session.add(created_user)
        #await self.session.commit()
        return created_user 
    
    async def get_by_email(self, email):
        stmt = select(User).where(
            and_(User.email == email, User.is_active == True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def updated_user_details(self, user_id, update_data: Update_user):
        user = await self.get_by_id(user_id)
        if not user:
            return None
        if update_data.username:
            user.username = update_data.username
        if update_data.email:
            user.email = update_data.email
        self.session.add(user)
        return user
    
    async def delete_user(self, user_id):
        user= await self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = False
        await self.session.commit()
        
    async def update_password(self, user_id, old_password, new_password):
        user = await self.get_by_id(user_id)
        if not user:
            return None
        if not verify_password(old_password, user.password):
            raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
        user.password = get_password_hash(new_password)
        await self.session.commit()
        return user
       
    async def get_all_users(self, last_id: UUID|None = None, page_size: int = 10):
        if last_id:
            stmt = select(User).where(and_(User.is_active == True, 
                                           User.id>last_id)).order_by(User.id).limit(page_size)
        else:
            stmt = select(User).where(User.is_active == True).order_by(User.id).limit(page_size)

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        next_last_id = None
        if users:
            next_last_id = (users[-1].id)
        
        return users, next_last_id 
    
    async def deleting_account(self, user_id):
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            await self.session.delete(user)
            stmt2 = select(Blog).where(Blog.author_id == user.id)
            result2 = await self.session.execute(stmt2)
        blog = result2.scalar_one_or_none()
        if blog:
            await self.session.delete(blog)

    async def blog_vector(self, search_text):
        query_vector = func.websearch_to_tsquery("english", search_text)
        stmt = select(Blog, 
                      func.ts_rank(Blog.search_vector, query_vector).label('rank')
                      ).where(
                          Blog.search_vector.op("@@")(query_vector)
                      ).order_by(
                          func.ts_rank(Blog.search_vector, query_vector).desc()
                      )
        result = await self.session.execute(stmt)
        return result.all()