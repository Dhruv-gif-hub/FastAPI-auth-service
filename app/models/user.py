from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated
from fastapi import Form

# This module defines the data models for user-related operations in the application.
class Users(BaseModel):
    username: Annotated[str, Form(...)]
    email: Annotated[EmailStr, Form(...)]
    full_name: str | None = None

# Model for representing a user in the database
class UserInDB(Users):
    hashed_password: Annotated[str, Form(...)]
    role: str
    posts: Annotated[list[str], Field(default_factory=list)] 

class signupUser(BaseModel):
    username: Annotated[str, Form(...)]
    password: Annotated[str, Form(...)]

class Update_user(BaseModel):
    username: Annotated[str | None, Form(...)] = None
    email: Annotated[EmailStr | None, Form(...)] = None

