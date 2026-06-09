from ..models.user import Update_user
from ..models.post import Blog_model
from ..repositories.user_repository import UserRepository
from ..dependencies.service_dependencies import get_user_repo, get_redis
from fastapi import Depends 
from typing import Annotated
 
# This act as a layer between the user and the database.
# From here the user's requests are mapped with the relevant database query function.
class UserService:
    
    def __init__(self, user_repo : Annotated[UserRepository, Depends(get_user_repo)], 
                redis = Depends(get_redis)):
        self.user_repo = user_repo
        self.redis = redis

    async def get_user_username(self, username):
        cached = await self.redis.get(f"user_username:{username}")
        if cached:
            return cached
        user = await self.user_repo.get_by_username(username)
        await self.redis.set(
            f"user_username:{username}",
            user,
            ex=3600
        )
        return user

    def profile_access(self, user):
        return user

    def post_creation(self, user, data : Blog_model, post):
        if data.author_id == user.id:
            result = post.create_blog(data)
            return {
                "Message": "Posted",
                "post": result
            }
        
    def posts(self, post, user):
        values = post.get_blogs_by_author(user.id)
        return values

    def update_profile(self, user, data : Update_user, user_repo : UserRepository):
        result = user_repo.updated_user_details(user.id, data)

        return {
            "Message": "Updated",
            "user": result
        }

    def update_password(self, user, user_repo : UserRepository,current_password: str,
                        new_password: str):
        result = user_repo.update_password(user.id, current_password, new_password)
        return {
            "Message": "Updated",
            "user":result
        }
    
    def get_all_users(self,user,user_repo,last_id, page_size):
        if user:
            return user_repo.get_all_users(last_id, page_size)
        return None
    
    def get_user(self,user, user_name,user_check):
        if user_check:
            cached = self.redis.get(f"user:{user_name}")
            if cached:
                return cached
            
            result = user.get_by_id(user_name)
            self.redis.set(f"user:{user_name}",
                           result,
                           ex = 3600)
        return None
    
    async def deleting_user(self, user_id):
        await self.redis.delete(f"user:{user_id}")
        return self.user_repo.deleting_account(user_id)
    
    async def soft_delete(self, user_id):
        await self.redis.delete(f"user:{user_id}")
        return self.user_repo.delete_user(user_id)
        

    def blog_vector(self, search_text : str):
        return self.user_repo.blog_vector(search_text)