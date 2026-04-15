from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated
from fastapi import Form
#from uuid import UUID , uuid4

class post(BaseModel):
    model_config = ConfigDict(strict = True, extra="forbid", validate_assignment=True)

    #pid: Annotated[UUID, Field(default_factory=uuid4)]
    Title: Annotated[str, Form(...)]
    Content: Annotated[str, Form(...)]


