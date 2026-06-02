from ..database.mongo import Comment
from ..models.post import Comment_model
from datetime import datetime

class CommentRepository:
    async def create(self, model: Comment_model):
        comment = Comment(
            blog_id=model.parent_blog_id,
            user_id=model.user_id,
            content=model.content,
            parent_comment_id=model.parent_comment_id
        )
        return await comment.insert()

    async def get_blog_comments(self,blog_id: str):
        return await Comment.find(
            Comment.blog_id == blog_id
        ).to_list()
    
    async def get_comment_by_id(self, comment_id: str):
        return await Comment.find(Comment.id == comment_id).to_list()
    
    async def delete_comment(self, comment_id):
        return await Comment.find_one(Comment.id == comment_id).delete()
    
    async def update_comment(self, comment_id, new_content):
        comment = await Comment.find_one(Comment.id == comment_id)
        if comment:
            comment.content = new_content
            comment.updated_at = datetime.now()
            await comment.save()
            return comment
        return None


