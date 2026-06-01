from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated
from fastapi import Depends
from ..dependencies.db import get_db
from sqlalchemy import select
from ..database.postgres import User

class UserRepository:

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db)]
    ):
        self.session = session

    async def get_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.commit()
        return user 