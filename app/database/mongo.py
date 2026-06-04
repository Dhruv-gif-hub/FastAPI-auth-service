from typing import List, Optional
from datetime import datetime
from beanie import Link, BackLink, DocumentWithSoftDelete, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ..models.post import ContentBlock
from uuid import UUID

class BlogContent(DocumentWithSoftDelete):

    blog_id: str

    content: list[ContentBlock]
    comments : List[BackLink["Comment"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field":"blog_content"} 
) 
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

class Comment(DocumentWithSoftDelete):

    blog_id: str
    user_id: UUID
    content: str = Field(
        min_length=1,
        max_length=5000
    )
    parent_comment_id: PydanticObjectId | None= None 
    blog_content : Optional[Link[BlogContent]] = None
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
        "mongodb://172.29.80.1:27017"
    )
    database = client["Blog_platform"]
    await init_beanie(
        database = database,
        document_models = [
            BlogContent,
            Comment
        ]
    )