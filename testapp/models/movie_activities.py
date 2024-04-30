from django.db import models
from .base_models import Subscription
from .movie import Movie
from .user import User


class Recommendations(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendations"
    )
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    is_positive = (
        models.BooleanField()
    )  # True - Рекомендация, False - Анти рекомендация
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        verbose_name_plural = "Recommendations"

    def __str__(self):
        return f"({self.id}) {self.user.nickname} -> movie id {self.movie.id}. Status: {self.is_positive}"


class SubscriptionToMovie(Subscription):
    target_movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        unique_together = ("subscriber", "target_movie")
        verbose_name_plural = "Subscriptions to movies"

    def __str__(self):
        return f"({self.id}) {self.subscriber.nickname} -> movie id - {self.target_movie.id}"
