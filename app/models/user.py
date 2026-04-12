from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi import Form

class Users(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class UserInDB(Users):
    hashed_password: str
    role: str

class signupUser(BaseModel):
    username: Annotated[str, Form(...)]
    password: Annotated[str, Form(...)]