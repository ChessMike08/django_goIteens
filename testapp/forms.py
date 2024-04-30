from django import forms
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from .models import *
from django.contrib.auth import get_user_model
from django.forms import NumberInput, TextInput, ValidationError, ModelForm


User = get_user_model()


class SignupForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = (
            "nickname",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "gender",
        )

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if nickname and User.objects.filter(nickname__iexact=nickname).exists():
            raise ValidationError("User with this nickname already exists")
        return nickname

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("User with this email already exists")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nickname = self.cleaned_data["nickname"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.gender = self.cleaned_data["gender"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "nickname",
        ]


class MovieForm(ModelForm):
    class Meta:
        model = Movie
        exclude = ("author_post", "slug", "trailers_youtube_code")


class ProductionAPIForm(ModelForm):
    search_input = forms.CharField(label="Search Input")
    is_full_name = forms.BooleanField(label="Is Full Name", required=False)

    class Meta:
        model = Production
        fields = ("search_input", "is_full_name")


class LanguageAPIForm(ModelForm):
    class Meta:
        model = Languages
        fields = ("code",)


class GenreForm(ModelForm):
    class Meta:
        model = Genre
        fields = "__all__"


class VideoForm(ModelForm):
    class Meta:
        model = Video
        exclude = ("movie",)


class HallForm(ModelForm):
    class Meta:
        model = Halls
        fields = "__all__"


class DateTimeLocalInput(TextInput):
    input_type = "datetime-local"


class SessionForm(forms.ModelForm):
    class Meta:
        model = Sessions
        fields = "__all__"
        widgets = {
            "start": DateTimeLocalInput(),
            "end": DateTimeLocalInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.fields["start"].initial = instance.start.strftime("%Y-%m-%dT%H:%M")
            self.fields["end"].initial = instance.end.strftime("%Y-%m-%dT%H:%M")


class BankForm(ModelForm):
    class Meta:
        model = Banks
        fields = "__all__"


class SeatsTypeForm(ModelForm):
    class Meta:
        model = SeatsTypes
        fields = "__all__"


class SeatForm(ModelForm):
    class Meta:
        model = Seats
        exclude = (
            "hall",
            "line_number",
        )
        widgets = {
            "row_number": NumberInput(attrs={"min": 1}),
        }


class UpdateSeatForm(ModelForm):
    class Meta:
        model = Seats
        exclude = (
            "hall",
            "row_number",
        )


class OrderDataForm(ModelForm):
    class Meta:
        model = OrderData
        exclude = ("user", "token", "paid", "created_at")


class ReservationForm(ModelForm):
    class Meta:
        model = Reservations
        exclude = ("created_at",)


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("comment", "rating")


class NewsForm(ModelForm):
    class Meta:
        model = News
        exclude = ("slug", "created_at", "updated_at", "author")


class PostForm(ModelForm):
    class Meta:
        model = Posts
        exclude = ("slug", "created_at", "updated_at", "author", "group")


class GroupForm(ModelForm):
    class Meta:
        model = Groups
        exclude = ("slug", "closed", "author", "parent_group")


class NewsCommentForm(ModelForm):
    class Meta:
        model = NewsComment
        exclude = (
            "user",
            "parent_comment",
            "created_at",
            "updated_at",
            "news",
        )


class PostCommentForm(ModelForm):
    class Meta:
        model = PostComment
        exclude = ("user", "post", "created_at", "updated_at")


class PrivateMessageForm(ModelForm):
    class Meta:
        model = PrivateMessages
        exclude = (
            "user",
            "created_at",
            "is_read",
            "updated_at",
            "parent_message",
            "chat",
        )


class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        exclude = (
            "user",
            "created_at",
            "is_read",
            "initiator",
            "related_object_id",
            "related_object_type",
        )
