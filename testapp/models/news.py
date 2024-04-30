from django.db import models
from .user import User
from .base_models import NewsAndPosts
from django.utils.text import slugify


class News(NewsAndPosts):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_news"
    )

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f'({self.id}) "{self.title}". Author "{self.author.nickname}"'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.author.nickname + "-" + self.title + "-" + self.content[:10]
            )
        super().save(*args, **kwargs)

    @property
    def total_likes(self):
        return self.likes.count()
