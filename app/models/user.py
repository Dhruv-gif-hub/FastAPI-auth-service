from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated
from fastapi import Form

class Users(BaseModel):
    username: Annotated[str, Form(...)]
    email: Annotated[EmailStr, Form(...)]
    full_name: str | None = None

class UserInDB(Users):
    hashed_password: Annotated[str, Form(...)]
    role: str
    posts: Annotated[list[str], Field(default_factory=dict)]

class signupUser(BaseModel):
    username: Annotated[str, Form(...)]
    password: Annotated[str, Form(...)]

class Update_user(BaseModel):
    username: Annotated[str | None, Form(...)] = None
    email: Annotated[EmailStr | None, Form(...)] = None

