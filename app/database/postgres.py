from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from uuid import uuid4, UUID
from datetime import datetime
from typing import List
from sqlalchemy.sql import func   
from sqlalchemy import Computed, Index, ForeignKey

engine = create_async_engine(
    "postgresql+asyncpg://postgres:Haldwani%401@172.29.80.1:5432/Blogs",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False
)

Session_local = async_sessionmaker(bind=engine,
                       autoflush=False,
                       autocommit=False
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "blog_data"}

    id: Mapped[UUID] = mapped_column(primary_key=True)

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid4()
        super().__init__(**kwargs)

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=True, nullable=False)
    role: Mapped[str] = mapped_column(default="user", nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


    blogs: Mapped[List["Blog"]] = relationship("Blog", 
                                               back_populates="author",
                                               lazy="selectin")


class Blog(Base):
    __tablename__ = "blogs"
    __table_args__ = {"schema": "blog_data"}

    id: Mapped[UUID] = mapped_column(primary_key=True)

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = uuid4()
        super().__init__(**kwargs)

    author_id: Mapped[UUID] = mapped_column(ForeignKey("blog_data.users.id"))
    mongo_content_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=func.now())

    search_vector: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR(),
        Computed("to_tsvector('english', title || ' ' ||  status)", persisted=True),
        index=False 
    )


    author: Mapped["User"] = relationship("User", 
                                          back_populates="blogs",
                                          lazy="selectin")
    __table_args__ = (
        Index("ix_news_search_vector", "search_vector", postgresql_using="gin"),
        {"schema": "blog_data"}
    )