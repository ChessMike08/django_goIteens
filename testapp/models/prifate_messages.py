from django.db import models
from django.core.exceptions import ValidationError
from .user import User
from .base_models import NotufucationAndMessage
from django.template.defaultfilters import slugify
from django.urls import reverse


class Chats(models.Model):
    slug = models.SlugField(unique=True)
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chats_as_user1"
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chats_as_user2"
    )

    @property
    def is_valid(self) -> bool:
        if self.user1 == self.user2:
            raise ValidationError("Users in a chat must be different.")
        return True

    class Meta:
        verbose_name_plural = "Chats"
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"], name="unique_chat_between_users"
            ),
        ]

    def get_absolute_url(self):
        return reverse("chat", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user1.nickname} {self.user2.nickname}")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'({self.id}) Slug: {self.slug}. Users: "{self.user1.nickname}", "{self.user2.nickname}" '


class PrivateMessages(NotufucationAndMessage):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name="messages")
    parent_message = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="replies"
    )  # На какое сообщение отвечает
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Private messages"

    def __str__(self):
        return f"({self.id}) Chat id - {self.chat.id}, parent message id - {self.parent_message.id}. Updated: {self.updated_at}"
