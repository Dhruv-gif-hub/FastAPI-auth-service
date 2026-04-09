from pydantic import BaseModel

class Users(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(Users):
    hashed_password: str

