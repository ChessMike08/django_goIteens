from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        first_name,
        last_name,
        nickname,
        phone_number,
        gender,
        password,
    ) -> "User":
        if not nickname:
            raise ValueError("A nickname is required.")
        if not email:
            raise ValueError("An email is requered.")
        if not password:
            raise ValueError("A password is required.")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            phone_number=phone_number,
            is_banned=False,
            ban_expiry=None,
            gender=gender,
            telegram_id=None,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        email,
        password,
        first_name,
        last_name,
        nickname,
        phone_number,
        gender,
    ) -> "User":
        if not nickname:
            raise ValueError("A nickname is required.")
        if not email:
            raise ValueError("An email is required.")
        if not password:
            raise ValueError("A password is required.")
        superuser = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            nickname=nickname,
            gender=gender,
        )
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.is_active = True
        superuser.is_verinfication = True

        superuser.save()
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    nickname = models.CharField(_("nick name"), max_length=150, unique=True)
    slug = models.SlugField(_("slug"), unique=True)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_banned = models.BooleanField(
        _("banned"),
        default=False,
        help_text=_("Checking if a user is banned."),
    )
    ban_expiry = models.DateTimeField(
        _("date ban ends"),
        default=None,
        null=True,
        help_text=_("The date when the ban ends for the user."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    gender = models.CharField(
        max_length=1,
        choices={"u": "unknown", "m": "male", "f": "female"},  # type: ignore
        default="u",  # "u": "unknown"
    )
    is_verinfication = models.BooleanField(
        _("verinfication"),
        default=False,
        help_text=_("Checking if a user been verinfected."),
    )
    last_action = models.DateTimeField(
        _("last action"),
        default=timezone.now,
        help_text=_("Date and time of last action."),
    )
    last_profile_edit = models.DateTimeField(
        _("last profile edit"), default=None, null=True
    )
    phone_number = models.CharField(_("phone number"), max_length=15, unique=True)
    notification_in_telegram = models.BooleanField(
        _("permission to send messages via bot"), default=False
    )
    telegram_id = models.IntegerField(_("telegram id"), null=True, unique=True)
    objects = UserManager()
    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "gender",
    ]

    def __str__(self):
        return f"({self.id}) {self.nickname}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nickname)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("profile", kwargs={"slug": self.slug})
