from pydantic import BaseModel, Field, EmailStr
from typing_extensions import Annotated
from fastapi import Form

# This module defines the data models for user-related operations in the application.
class Users(BaseModel):
    username: Annotated[str, Form(...)]
    email: Annotated[EmailStr, Form(...)]

# Model for representing a user in the database
class UserInDB(Users):
    hashed_password: Annotated[str, Form(...)]
    role: str

# Model for user signup, which includes only the necessary fields for creating a new user
class signupUser(BaseModel):
    username: Annotated[str, Form(...)]
    password: Annotated[str, Form(...)]

# Model for updating user information, allowing optional fields for username and email
class Update_user(BaseModel):
    username: Annotated[str | None, Form(...)] = None
    email: Annotated[EmailStr | None, Form(...)] = None

