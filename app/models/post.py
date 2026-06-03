from pydantic import BaseModel, ConfigDict
from typing_extensions import Annotated, Literal
from fastapi import Form
from uuid import UUID
from bson import ObjectId

class ContentBlock(BaseModel):
    type: Literal[
        "heading",
        "paragraph"
    ] = Form(..., description="Type of content block, either 'heading' or 'paragraph'")

    text: str = Form(..., description="Text content of the block")

class Blog_model(BaseModel):
    model_config = ConfigDict(strict = True, extra="forbid", validate_assignment=True)

    author_id: Annotated[UUID, Form(...)]
    mongo_content_id: Annotated[str, Form(...)] # blog_id in mongodb
    Title: Annotated[str, Form(...)]
    status: Annotated[str, Form(...)]
    Content: list[ContentBlock]

class Blog_update(BaseModel):
    model_config = ConfigDict(strict = True, extra="forbid", validate_assignment=True)

    Title: Annotated[str|None, Form(...)] = None
    status: Annotated[str|None, Form(...)] = None
    Content: list[ContentBlock] | None = None
    
class Comment_model(BaseModel):
    model_config = ConfigDict(strict = True, extra="forbid", validate_assignment=True)

    parent_blog_id: Annotated[str, Form(...)] # blog_id in mongodb
    user_id: Annotated[UUID, Form(...)]
    content: Annotated[str, Form(..., description="Content can have at maximum 5000 characters")]
    parent_comment_id: Annotated[ObjectId | None, Form(...)] = None


