from django.db import models
from .user import User


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=5000)
    rating = models.IntegerField(
        choices=[
            (1, "Too bad"),
            (2, "Bad"),
            (3, "Satisfactory"),
            (4, "Good"),
            (5, "Great"),
        ],
    )
    hide = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(
        "Movie", on_delete=models.CASCADE, null=True, related_name="comments"
    )
    session = models.ForeignKey(
        "Sessions", on_delete=models.CASCADE, null=True, related_name="comments"
    )

    def __str__(self):
        if self.movie:
            target = f"Movie id: {self.movie.id}"
        elif self.session:
            target = f"Session id: {self.session.id}"
        else:
            target = "Unknown target (ERROR)"
        return f'({self.id}) User: "{self.user.nickname}", rating: {self.rating}. To: {target}'
