from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from beanie import Document
from pydantic import Field
from bson import ObjectId
from pymongo import IndexModel
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

class ContentBlock(BaseModel):
    type: Literal[
        "heading",
        "paragraph"
    ]

    text: str

class BlogContent(Document):

    blog_id: str

    content: list[ContentBlock]

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )

    class Settings:
        name = "blog_contents"
        indexes = [
        IndexModel(
            "blog_id",
            unique=True
        )
    ]

class Comment(Document):

    blog_id: str

    user_id: str

    content: str = Field(
        min_length=1,
        max_length=5000
    )

    parent_comment_id: ObjectId | None= None

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )

    class Settings:
        name = "comments"

        indexes = [
        IndexModel("blog_id"),
        IndexModel("user_id"),
        IndexModel("parent_comment_id")
    ]
        

async def init_mongodb() -> None:
    client = AsyncIOMotorClient(
        "mongodb://localhost:27017"
    )

    database = client["blog_platform"]

    await init_beanie(
        database = database,
        document_models = [
            BlogContent,
            Comment
        ]
    )