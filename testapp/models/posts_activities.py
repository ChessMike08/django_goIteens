from django.db import models
from .base_models import NewsAndPostsComments
from .posts import Posts


class PostComment(NewsAndPostsComments):
    post = models.ForeignKey(
        Posts, on_delete=models.CASCADE, null=True, related_name="comments"
    )

    class Meta:
        verbose_name_plural = "Posts comments"

    def __str__(self):
        return f"({self.id}) {self.user.nickname}, {self.post.id}"
