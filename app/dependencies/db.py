from ..database.postgres import Session_local

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

