from fastapi import HTTPException
from fastapi import status
from ..models.user import UserInDB
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

    def delete_data(self, username: str):
        if username not in self.file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
        del self.file[username]
        
fake_db = Database()