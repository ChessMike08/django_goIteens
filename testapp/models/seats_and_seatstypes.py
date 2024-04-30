from django.db import models
from .session_and_order import Halls


class SeatsTypes(models.Model):
    name = models.CharField(max_length=225)
    price = models.IntegerField()

    class Meta:
        verbose_name_plural = "Seats types"

    def __str__(self):
        return f"({self.id}) {self.name}, {self.price}"


class Seats(models.Model):
    hall = models.ForeignKey(Halls, on_delete=models.CASCADE)
    row_number = models.IntegerField()
    line_number = models.IntegerField()
    active = models.BooleanField(default=True)
    seat_type = models.ForeignKey(SeatsTypes, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Seats"

    def __str__(self):
        return f'({self.id}) Hall "{self.hall.name}". Row: {self.row_number}, line: {self.line_number}. Type "{self.seat_type.name}"'
