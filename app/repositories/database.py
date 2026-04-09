from http.client import HTTPException
from fastapi import status

class Database():
    def __init__(self):
        self.file = {}

    def upload_data(self, data: dict):
        if data["username"] in self.file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        self.file.update(data)

    def delete_data(self, username: str):
        if username not in self.file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
        
fake_db = Database()