from pydantic import BaseModel, ConfigDict
from .post import ContentBlock
class BlogResponse(BaseModel):
    model_config = ConfigDict(strict = True, extra="forbid", validate_assignment=True)

    id: str
    author_id: str
    title:str
    status: str
    content: list[ContentBlock]