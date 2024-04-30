from django.db import models
from .user import User
from .base_models import NewsAndPosts


class Groups(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    parent_group = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="under_group"
    )
    closed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Posts groups"

    def __str__(self):
        return f'({self.id}) {self.name}, slug: "{self.slug}". Parent group id - "{self.parent_group.id}"'


class Posts(NewsAndPosts):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_posts"
    )
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name="posts")

    class Meta:
        verbose_name_plural = "Posts"

    def __str__(self):
        return f'({self.id}) "{self.title}". Author "{self.author.nickname}", group id - {self.group.id}'
