import re
from django.db import models
from django.core.validators import MinLengthValidator, FileExtensionValidator

from .user import User
from django.utils.translation import gettext_lazy as _
from .base_models import RatingMixin
from django.template.defaultfilters import slugify
from django.urls import reverse

from .allowed_extensions_video import allowed_extensions_video


class Languages(models.Model):
    code = models.CharField(unique=True)
    english_name = models.CharField()
    native_name = models.CharField(null=True)

    class Meta:
        verbose_name_plural = "Languages"

    def __str__(self):
        return f"({self.id}) {self.english_name} ({self.native_name}), {self.code}"


class Production(models.Model):
    common_place_english_name = models.CharField(max_length=500)
    official_place_english_name = models.CharField(max_length=500)
    common_place_native_name = models.CharField(max_length=500, null=True)
    official_place_native_name = models.CharField(max_length=500, null=True)
    capital = models.CharField(unique=True, null=True)
    region = models.CharField(null=True)
    translations = models.JSONField(null=True)
    cca2 = models.CharField(unique=True, null=True)
    ccn3 = models.CharField(unique=True, null=True)
    cca3 = models.CharField(unique=True, null=True)
    cioc = models.CharField(unique=True)
    flag_emoji = models.CharField(null=True, unique=True)
    flag_png = models.URLField(null=True)
    flag_svg = models.URLField(null=True)
    flag_alt = models.CharField(null=True)
    google_maps = models.URLField(null=True)
    timezones = models.CharField(null=True)
    postal_code_format = models.CharField(null=True)
    postal_code_regex = models.CharField(null=True)

    def __str__(self):
        return f"({self.id}) {self.cioc}, {self.common_place_english_name}"


class Movie(RatingMixin):
    title = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    slug = models.SlugField(
        unique=True, help_text=_("Slug-url. You can leave it blank.")
    )
    director = models.CharField(max_length=100)
    production = models.ManyToManyField(Production, related_name="movies")
    release_date = models.DateField(null=True)  # уведомление о начале продаж в тг ?
    year = models.IntegerField(help_text=_("Year of the film."))
    hire_end = models.DateField(null=True, help_text=_("Sales closing date."))
    duration = models.PositiveIntegerField(help_text=_("Length of time (in minutes)."))
    description = models.TextField(null=True, help_text=_("Film description."))
    starring = models.TextField(null=True, help_text=_("In the lead roles."))
    min_age = models.PositiveIntegerField(
        help_text=_("Minimum acceptable age to watch the film."),
    )
    poster = models.ImageField(upload_to="posters/", null=True)
    trailer = models.URLField(null=True)
    trailers_youtube_code = models.CharField(null=True)
    author_post = models.ForeignKey(User, on_delete=models.CASCADE)
    genres = models.ManyToManyField("Genre", related_name="movies")

    def get_absolute_url(self):
        return reverse("movie_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.trailer and "youtube.com" in self.trailer:
            youtube_regex = r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:(?:watch\?v=)|(?:embed/))|youtu\.be/)([a-zA-Z0-9_-]+)"
            match = re.search(youtube_regex, self.trailer)
            if match:
                self.trailers_youtube_code = match.group(1)
        else:
            self.trailers_youtube_code = None

        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"({self.id}) {self.title}, slug: {self.slug}."


class Video(models.Model):
    file = models.FileField(
        upload_to="videos/",
        validators=[
            FileExtensionValidator(allowed_extensions=allowed_extensions_video)
        ],
    )
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="videos")

    def __str__(self):
        return f"({self.id}) {self.language.english_name}, {self.movie.title}."


class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"({self.id}) {self.name}"
