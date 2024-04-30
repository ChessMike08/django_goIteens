from django.db import models
from .user import User
from .news import News
from .base_models import NewsAndPostsComments


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "news")

    def __str__(self):
        return f'({self.id}) User "{self.user.nickname}" liked news id - {self.news.id}'


class NewsComment(NewsAndPostsComments):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="replies"
    )

    class Meta:
        verbose_name_plural = "News comments"

    def __str__(self):
        return f"({self.id}) {self.user.nickname}, {self.new.id}. Parent comment id - {self.parent_comment.id}"
