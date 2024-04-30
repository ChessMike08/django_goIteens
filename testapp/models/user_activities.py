from django.db import models
from .user import User
from .base_models import Subscription, NotufucationAndMessage


class SubscriptionToUser(Subscription):
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        verbose_name_plural = "Subscriptions to users"
        unique_together = ("subscriber", "target_user")

    def __str__(self):
        return f"({self.id}) {self.subscriber.nickname} -> {self.target_user.nickname}"


class UsersBlacklists(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users_in_your_blacklist"
    )
    user_banned = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Юзер которого блокнули

    class Meta:
        unique_together = ("user", "user_banned")
        verbose_name_plural = "Users black lists"

    def __str__(self):
        return f"({self.id}) {self.user.nickname} blocked {self.user_banned.nickname}"


class Notification(NotufucationAndMessage):
    related_object_id = models.PositiveIntegerField()  # ID связанного объекта
    related_object_type = models.CharField(max_length=50)  # Класс связанного объекта
    initiator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="initiated_notifications"
    )  # Юзер который спровоцировал отправку

    class Meta:
        verbose_name_plural = "Users notifications"

    def __str__(self):
        return f'({self.id}) Obj_id - {self.related_object_id}, Obj_type - "{self.related_object_type}". Where user - "{self.user.nickname}"'
