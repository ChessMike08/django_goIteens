from django.db import models
from .movie import Movie
from .user import User
from secured_fields import EncryptedCharField
from .base_models import RatingMixin


class Halls(models.Model):
    name = models.CharField(max_length=200, unique=True)
    worker = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Halls"

    def __str__(self):
        return f"({self.id}) {self.name}, worker - {self.worker}"


class Sessions(RatingMixin):
    hall = models.ForeignKey(Halls, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f'({self.id}) Hall "{self.hall.name}", movie "{self.movie.title}"({self.movie.id})'


class Banks(models.Model):
    name = models.CharField(max_length=225, unique=True)
    href_on_official_site = models.URLField(unique=True)
    payment_accepted = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Banks"

    def __str__(self):
        return f"({self.id}) {self.name}. {self.href_on_official_site}, {self.payment_accepted}"


class OrderData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE)
    card_number = EncryptedCharField(max_length=16)
    token = EncryptedCharField()
    paid = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Datas in orders"

    def __str__(self):
        return f"({self.id}) {self.user.nickname}, {self.bank.name}. Cart: {self.card_number}, created at: {self.created_at}"


class Reservations(models.Model):
    order = models.ForeignKey(OrderData, on_delete=models.CASCADE)
    seat = models.ForeignKey("Seats", on_delete=models.CASCADE)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reservations"
        unique_together = ("seat", "session")

    def __str__(self):
        return f"({self.id}) Order id - {self.order.id}"
