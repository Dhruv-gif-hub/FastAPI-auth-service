from fastapi import HTTPException
from fastapi import status
from ..models.user import UserInDB
from uuid import UUID , uuid4

class Database():
    def __init__(self):
        self.file = {}
        
    def get_user(self, username: str):
        user_dict = self.file.get(username)

        if not user_dict:
            return None

        return UserInDB(**user_dict)
    
    def upload_data(self,username: str, data: dict):
        if data["username"] in self.file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        self.file[username] = data
        self.file[username]["User_id"] = str(uuid4)
        self.file[username]["is_active"] = True

    def delete_data(self, username: str):
        if username not in self.file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
        del self.file[username]

    def posting(self, username : str, post_data: dict):
        user_data = self.file[username]
        user_data["posts"] = post_data
        user_data["posts"]["pid"] = str(uuid4)

    def post_access(self, username : str):
        profile_data = self.file[username]
        return profile_data["posts"]
    
    def update(self, username: str, value:str, updated_data: str):
        self.file[username][value] = updated_data
        if value == "username":
            self.file[updated_data] = self.file.pop(username)

    def admin_role(self, username: str):
        self.file[username]["role"] = "admin"

    def deactivating_account(self, username: str):
        self.file[username]["is_active"] = False

fake_db = Database()