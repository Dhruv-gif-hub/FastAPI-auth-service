from ..database.mongo import Comment
from ..models.post import Comment_model

class CommentRepository:
    async def create(self, model: Comment_model):
        comment = Comment(
            blog_id=model.parent_blog_id,
            user_id=model.user_id,
            content=model.content,
            parent_comment_id=model.parent_comment_id
        )
        return await comment.insert()

async def get_blog_comments(
    self,
    blog_id: str
):
    return await Comment.find(
        Comment.blog_id == blog_id
    ).to_list()

