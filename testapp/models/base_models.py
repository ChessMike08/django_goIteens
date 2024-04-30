from decimal import Decimal
from django.db import models
from django.db.models import Avg

from .user import User


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    action_alerts = models.BooleanField(default=True)

    class Meta:
        abstract = True


class RatingMixin(models.Model):
    @property
    def rating(self) -> float:
        comments = self.comments.all()
        if comments.exists():
            avg_rating = comments.aggregate(avg_rating=Avg("rating"))["avg_rating"]
            return avg_rating or Decimal("0.0")
        else:
            return Decimal("0.0")

    class Meta:
        abstract = True


class NewsAndPosts(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NewsAndPostsComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NotufucationAndMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    class Meta:
        abstract = True
