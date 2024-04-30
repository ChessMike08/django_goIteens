from datetime import timedelta
import json
import secrets
from django.http import JsonResponse
from psycopg2.errors import UniqueViolation
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy as _
from django.views.generic import View, FormView, DetailView, UpdateView
from django.utils import timezone
from django.contrib.auth import login, logout
from testapp.access_mixin import IsLoging, IsAdmin, IsYourReservation
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from testapp.forms import *
from testapp.models.apis.custom_api_errors import CustomAPIError

from .models.apis.country_api_def import (
    search_by_code,
    search_by_name_or_fullname,
    search_by_region,
    search_all,
)

from .models.apis.language_api_def import get_data_lang_on_code, get_data_all_lang

from .models import *


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def my_profile_redirect(request):
    slug = request.user.slug
    profile_url = reverse("profile", kwargs={"slug": slug})
    return redirect(profile_url)


class MainView(View):
    def get(self, request, *args, **kwargs):
        new_user_list = User.objects.order_by("-date_joined")[:10]
        last_news_list = News.objects.order_by("-created_at")[:10]
        last_posts_list = Posts.objects.filter(group__closed=False).order_by(
            "-created_at"
        )[:10]
        last_news_comments = NewsComment.objects.all().order_by("-created_at")[:10]
        last_post_comments = PostComment.objects.all().order_by("-created_at")[:10]
        all_movie_for_sale = Movie.objects.filter(
            hire_end__gte=timezone.now(), release_date__lte=timezone.now()
        )
        paginator = Paginator(all_movie_for_sale, 2)
        page_number = request.GET.get("page")
        try:
            all_movie_for_sale_paginated = paginator.page(page_number)
        except PageNotAnInteger:
            all_movie_for_sale_paginated = paginator.page(1)
        except EmptyPage:
            all_movie_for_sale_paginated = paginator.page(paginator.num_pages)
        context = {
            "new_user_list": new_user_list,
            "last_news_list": last_news_list,
            "last_posts_list": last_posts_list,
            "all_movie_for_sale": all_movie_for_sale_paginated,
            "last_news_comments": last_news_comments,
            "last_post_comments": last_post_comments,
        }
        return render(request, "testapp/index.html", context=context)


class SignupView(FormView):
    template_name = "testapp/signup.html"
    model = User
    form_class = SignupForm
    success_url = _("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AuthenticationView(FormView):
    template_name = "testapp/signin.html"
    model = User
    form_class = LoginForm
    success_url = _("main_page")

    def form_valid(self, form):
        login(self.request, form.user_cache)
        return super().form_valid(form)


class ProfileView(DetailView):
    template_name = "testapp/profile.html"
    model = User
    content_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        user = get_object_or_404(User, slug=slug)
        recommendations = Recommendations.objects.filter(user=user)
        authored_posts = Posts.objects.filter(author=user)
        context["recommendations"] = recommendations
        context["authored_posts"] = authored_posts
        if self.request.user.is_authenticated and self.request.user != user:
            subscription = SubscriptionToUser.objects.filter(
                subscriber=self.request.user, target_user=user
            ).first()
            context["subscription"] = subscription
        context["current_time"] = timezone.now()
        user_banned = UsersBlacklists.objects.filter(user_banned=user)
        context["user_banned"] = user_banned
        return context


class EditProfileView(IsLoging, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "testapp/all_fields_form.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        if self.object.last_profile_edit:
            time_since_last_edit = timezone.now() - self.object.last_profile_edit
            if time_since_last_edit < timedelta(days=1):
                messages.error(
                    request, "You can only edit your profile once every 24 hours."
                )
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.last_profile_edit = timezone.now()
        user.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Edit profile"
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return _("profile", kwargs={"slug": self.request.user.slug})


class PasswordChangeCustomView(IsLoging, PasswordChangeView):
    model = User
    template_name = "testapp/all_fields_form.html"
    success_url = _("logout")

    def form_valid(self, form):
        response = super().form_valid(form)
        logout(self.request)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Change Password"
        context["finishing"] = (
            "After changing the password, you will be logged out and will need to log in again."
        )
        return context


class CreateSubscriptionToUserView(View):
    def post(self, request, slug):
        action_alerts = request.POST.get("action_alerts") == "true"
        target_user = get_object_or_404(User, slug=slug)
        subscription, created = SubscriptionToUser.objects.get_or_create(
            subscriber=request.user,
            target_user=target_user,
            defaults={"action_alerts": action_alerts},
        )
        if not created:
            subscription.action_alerts = action_alerts
            subscription.save()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class DeleteSubscriptionToUserView(View):
    def post(self, request, subscription_to_user_id):
        subscription_to_user = get_object_or_404(
            SubscriptionToUser, id=subscription_to_user_id
        )
        if self.request.user == subscription_to_user.subscriber:
            subscription_to_user.delete()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class CreateUserToBlacklistView(View):
    def post(self, request, slug):
        user_banned = get_object_or_404(User, slug=slug)
        try:
            UsersBlacklists.objects.create(
                user=request.user,
                user_banned=user_banned,
            )
        except IntegrityError:
            pass
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class DeleteUserToBlacklistView(View):
    def post(self, request, slug):
        ban = get_object_or_404(UsersBlacklists, user_banned__slug=slug)
        if self.request.user == ban.user:
            ban.delete()
        else:
            pass
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class MovieFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = MovieForm

    def form_valid(self, form):
        form.instance.author_post = self.request.user
        self.movie = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add movie"
        return context

    def get_success_url(self):
        return _("details_movie", kwargs={"slug": self.movie.slug})


class MovieUpdateView(IsAdmin, UpdateView):
    model = Movie
    template_name = "testapp/all_fields_form.html"
    form_class = MovieForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Edit movie"
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(slug=self.kwargs["slug"])

    def form_valid(self, form):
        form.instance.author_post = self.request.user
        self.movie = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_movie", kwargs={"slug": self.movie.slug})


class MovieDetailView(DetailView):
    model = Movie
    template_name = "testapp/detail_movie.html"
    content_object_name = "movie"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        comments = Comment.objects.filter(movie=movie).order_by("-created_at")
        recommendations = Recommendations.objects.filter(movie=movie)
        user = self.request.user
        user_recommendation = None
        if user.is_authenticated:
            user_recommendation = recommendations.filter(user=user).first()
            subscription = SubscriptionToMovie.objects.filter(
                subscriber=self.request.user, target_movie=movie
            ).first()
        context["comments"] = comments
        context["comment_form"] = CommentForm()
        context["recommendations"] = recommendations
        context["user_recommendation"] = user_recommendation
        context["subscription"] = subscription
        return context


class AddCommentView(IsLoging, View):
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            if "movie_slug" in kwargs:
                movie = Movie.objects.get(slug=kwargs["movie_slug"])
                comment.movie = movie
            elif "session_id" in kwargs:
                session = Sessions.objects.get(id=kwargs["session_id"])
                comment.session = session
            comment.save()
            next_page = request.POST.get("next_page")
            return redirect(next_page) if next_page else redirect("main_page")


class CreateSubscriptionToMovieView(IsLoging, View):
    def post(self, request, movie_slug):
        action_alerts = request.POST.get("action_alerts") == "true"
        target_movie = get_object_or_404(Movie, slug=movie_slug)
        subscription, created = SubscriptionToMovie.objects.get_or_create(
            subscriber=request.user,
            target_movie=target_movie,
            defaults={"action_alerts": action_alerts},
        )
        if not created:
            subscription.action_alerts = action_alerts
            subscription.save()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class DeleteSubscriptionToMovieView(IsLoging, View):
    def post(self, request, subscription_to_movie_id):
        subscription_to_movie = get_object_or_404(
            SubscriptionToMovie, id=subscription_to_movie_id
        )
        if self.request.user == subscription_to_movie.subscriber:
            subscription_to_movie.delete()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class AddRecommendationView(IsLoging, View):
    def post(self, request, *args, **kwargs):
        movie_id = request.POST.get("movie_id")
        recommendation_value = request.POST.get("recommendation")
        is_positive = recommendation_value.lower() == "true"
        user = request.user
        movie = get_object_or_404(Movie, id=movie_id)
        recommendation, created = Recommendations.objects.get_or_create(
            user=user, movie=movie, defaults={"is_positive": is_positive}
        )
        if not created:
            recommendation.is_positive = is_positive
            recommendation.save()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class DeleteRecommendationView(IsLoging, View):
    def post(self, request, recommendation_id):
        recommendation = get_object_or_404(Recommendations, id=recommendation_id)
        if self.request.user == recommendation.user:
            recommendation.delete()
        else:
            pass
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class ProductionFormAPIView(IsAdmin, FormView):
    template_name = "testapp/form-api_production.html"
    form_class = ProductionAPIForm
    success_url = _("production_add_api")

    def form_valid(self, form):
        country_data = None

        is_search_by_name = self.request.POST.get("search_by_name")
        is_search_by_code = self.request.POST.get("search_by_code")
        is_search_by_region = self.request.POST.get("search_by_region")
        is_search_and_save_all = self.request.POST.get("search_and_save_all")
        is_full_name = form.cleaned_data.get("is_full_name")

        search_input: str = self.request.POST.get("search_input")

        try:
            if is_search_by_name:
                countries = search_by_name_or_fullname(search_input, is_full_name)
            elif is_search_by_code:
                countries = search_by_code(search_input)
            elif is_search_by_region:
                countries = search_by_region(search_input)
            elif is_search_and_save_all:
                countries = search_all()
        except CustomAPIError as e:
            messages.error(self.request, f"Error: {e}")

        for country_data in countries:
            capital = country_data.get("capital")
            capital = capital[0] if bool(capital) else None

            postal_code: dict = country_data.get("postalCode")
            if postal_code:
                postal_code_format = postal_code.get("format")
                postal_code_regex = postal_code.get("regex")
            else:
                postal_code_format = None
                postal_code_regex = None
            try:
                Production.objects.create(
                    common_place_english_name=country_data["name"]["common"],
                    official_place_english_name=country_data["name"]["official"],
                    common_place_native_name=list(
                        country_data["name"]["nativeName"].values()
                    )[0]["common"],
                    official_place_native_name=list(
                        country_data["name"]["nativeName"].values()
                    )[0]["official"],
                    capital=capital,
                    region=country_data["region"],
                    translations=json.dumps(
                        country_data["translations"], cls=DjangoJSONEncoder
                    ),
                    cca2=country_data.get("cca2"),
                    ccn3=country_data.get("ccn3"),
                    cca3=country_data.get("cca3"),
                    cioc=country_data.get("cioc"),
                    flag_emoji=country_data.get("flag"),
                    flag_png=country_data["flags"].get("png"),
                    flag_svg=country_data["flags"].get("svg"),
                    flag_alt=country_data["flags"].get("alt"),
                    google_maps=country_data["maps"]["googleMaps"],
                    timezones=country_data.get("timezones"),
                    postal_code_format=postal_code_format,
                    postal_code_regex=postal_code_regex,
                )
            except UniqueViolation as e:
                messages.error(self.request, f"Error: {e}")
            except IntegrityError:
                pass
        messages.success(self.request, "Countrie(s) added successfully.")
        return super().form_valid(form)


class LanguageFormAPIView(IsAdmin, FormView):
    template_name = "testapp/form-api_language.html"
    form_class = LanguageAPIForm
    success_url = _("language_add_api")

    def form_valid(self, form):
        languages_data = None

        is_search_by_code = self.request.POST.get("search_by_code")
        is_search_and_save_all = self.request.POST.get("search_and_save_all")

        lang_code: str = self.request.POST.get("code")

        try:
            if is_search_by_code:
                languages_data = get_data_lang_on_code(lang_code)
            elif is_search_and_save_all:
                languages_data = get_data_all_lang()
        except CustomAPIError as e:
            messages.error(self.request, f"Error: {e}")
        for language_data in languages_data["data"]:
            try:
                Languages.objects.create(
                    code=language_data["langCode"],
                    english_name=language_data["langEnglishName"],
                    native_name=language_data["langNativeName"],
                )
            except UniqueViolation as e:
                messages.error(self.request, f"Error: {e}")
            except IntegrityError:
                pass
        messages.success(self.request, "Language(s) added successfully.")
        return super().form_valid(form)


class GenreFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = GenreForm
    success_url = _("genre_add")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add genre"
        return context

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        description = form.cleaned_data["description"]
        if not description:
            description = None
        Genre.objects.create(name=name, description=description)
        return super().form_valid(form)


class HallFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = HallForm
    success_url = _("hall_add")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add hall"
        return context

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        worker = form.cleaned_data["worker"]
        Halls.objects.create(name=name, worker=worker)
        return super().form_valid(form)


class VideoFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = VideoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add video"
        return context

    def form_valid(self, form):
        self.video = form.save(commit=False)
        self.video.movie = Movie.objects.get(slug=self.kwargs["slug"])
        self.video.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_movie", kwargs={"slug": self.video.movie.slug})


class SeatsTypeFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = SeatsTypeForm
    success_url = _("seats_type_add")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        price = form.cleaned_data["price"]
        SeatsTypes.objects.create(name=name, price=price)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add seats type"
        return context


class BankFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = BankForm
    success_url = _("bank_add")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        href_on_official_site = form.cleaned_data["href_on_official_site"]
        payment_accepted = form.cleaned_data["payment_accepted"]
        Banks.objects.create(
            name=name,
            href_on_official_site=href_on_official_site,
            payment_accepted=payment_accepted,
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add bank data"
        return context


class NewsFormView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = NewsForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.news = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add news"
        return context

    def get_success_url(self):
        return _("details_news", kwargs={"slug": self.news.slug})


class NewsUpdateView(IsAdmin, UpdateView):
    model = News
    template_name = "testapp/all_fields_form.html"
    form_class = NewsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Edit news"
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(slug=self.kwargs["slug"])

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.news = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_news", kwargs={"slug": self.news.slug})


class NewsDetailsView(DetailView):
    model = News
    template_name = "testapp/detail_news.html"
    content_object_name = "news"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = self.get_object()
        comments = NewsComment.objects.filter(news=news).order_by("-created_at")
        context["comments"] = comments
        context["comment_form"] = NewsCommentForm()
        return context


class AddNewsCommentView(View):
    def post(self, request, *args, **kwargs):
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            newscomment = form.save(commit=False)
            newscomment.user = request.user
            news = News.objects.get(slug=kwargs["news_slug"])
            newscomment.news = news
            parent_comment_id = request.POST.get("parent_comment_id")
            if parent_comment_id:
                newscomment.parent_comment = NewsComment.objects.get(
                    id=parent_comment_id
                )
            newscomment.save()
            next_page = request.POST.get("next_page")
            return redirect(next_page) if next_page else redirect("main_page")


class CreateNotification(View):
    def post(self, request):
        related_object_id = request.POST.get("related_object_id")
        related_object_type = request.POST.get("related_object_type")
        initiator_id = request.POST.get("initiator_id")
        initiator = get_object_or_404(User, id=initiator_id)
        try:
            Notification.objects.create(
                related_object_id=related_object_id,
                related_object_type=related_object_type,
                initiator=initiator,
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class AddHallSeatView(IsAdmin, FormView):
    template_name = "testapp/add_or_change_hall_seats.html"
    form_class = SeatForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hall_id = self.kwargs["hall_id"]
        hall = get_object_or_404(Halls, id=hall_id)
        seats = Seats.objects.filter(hall=hall)
        context["seats"] = seats
        seats_by_row = {}
        for seat in seats:
            if seat.row_number not in seats_by_row:
                seats_by_row[seat.row_number] = []
            seats_by_row[seat.row_number].append(seat)
        context["hall"] = hall
        context["seats_by_row"] = seats_by_row
        return context

    def form_valid(self, form, *args, **kwargs):
        hall = get_object_or_404(Halls, id=self.kwargs["hall_id"])
        row_number = form.cleaned_data["row_number"]
        try:
            the_bigest_row_number = (
                Seats.objects.filter(hall=hall)
                .order_by("-row_number")
                .first()
                .row_number
            )
        except Exception:
            the_bigest_row_number = 0
        if (int(row_number) - 1) > the_bigest_row_number:
            return self.form_invalid(form)
        latest_seat = (
            Seats.objects.filter(row_number=row_number, hall=hall)
            .order_by("-line_number")
            .first()
        )
        if latest_seat:
            form.instance.line_number = latest_seat.line_number + 1
        else:
            form.instance.line_number = 1
        form.instance.hall = hall
        self.seat = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("add_or_change_hall_seat", kwargs={"hall_id": self.seat.hall.id})


class UpdateHallSeatView(IsAdmin, UpdateView):
    model = Seats
    template_name = "testapp/all_fields_form.html"
    form_class = UpdateSeatForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Edit seat"
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(id=self.kwargs["seat_id"])

    def form_valid(self, form):
        line_number = int(form.cleaned_data["line_number"])
        old_obj = self.get_object()
        hall = old_obj.hall
        row_number = old_obj.row_number
        old_line_number = old_obj.line_number
        the_bigest_line_number = (
            Seats.objects.filter(hall=hall, row_number=row_number)
            .order_by("-line_number")
            .first()
            .line_number
        )
        if line_number > the_bigest_line_number:
            return self.form_invalid(form)
        if old_line_number > line_number:
            seats_to_update = Seats.objects.filter(
                hall=hall,
                row_number=row_number,
                line_number__gte=line_number,
                line_number__lte=old_line_number,
            )
            for seat_to_update in seats_to_update:
                seat_to_update.line_number += 1
                seat_to_update.save()
                continue
        elif old_line_number < line_number:
            seats_to_update = Seats.objects.filter(
                hall=hall,
                row_number=row_number,
                line_number__gt=old_line_number,
                line_number__lte=line_number,
            )
            for seat_to_update in seats_to_update:
                seat_to_update.line_number -= 1
                seat_to_update.save()
                continue
        self.seat = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("add_or_change_hall_seat", kwargs={"hall_id": self.seat.hall.id})


class DeleteHallSeatView(IsAdmin, View):
    def post(self, request, seat_id):
        seat = get_object_or_404(Seats, id=seat_id)
        seats_to_update = Seats.objects.filter(
            hall=seat.hall,
            row_number=seat.row_number,
            line_number__gt=seat.row_number,
        )
        for seat_to_update in seats_to_update:
            seat_to_update.line_number -= 1
            seat_to_update.save()
            continue
        seat.delete()
        next_page = request.POST.get("next_page")
        return redirect(next_page) if next_page else redirect("main_page")


class AddSessionView(IsAdmin, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = SessionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add session"
        return context

    def form_valid(self, form):
        session = form.save(commit=False)
        hall = session.hall
        start = session.start
        end = session.end
        overlapping_sessions = Sessions.objects.filter(
            hall=hall, start__lt=end, end__gt=start
        )
        if overlapping_sessions.exists():
            messages.error(
                self.request,
                "Another session is already scheduled in this hall during this time.",
            )
            return self.form_invalid(form)
        self.session = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_session", kwargs={"session_id": self.session.id})


class SessionDetailView(DetailView):
    model = Sessions
    template_name = "testapp/detail_session.html"
    context_object_name = "session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        comments = Comment.objects.filter(session=session).order_by("-created_at")
        context["comments"] = comments
        context["comment_form"] = CommentForm()
        context["session"] = session
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(id=self.kwargs["session_id"])


class UpdateSessionView(IsAdmin, UpdateView):
    model = Sessions
    template_name = "testapp/all_fields_form.html"
    form_class = SessionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Edit session"
        return context

    def get_object(self, queryset=None):
        return self.model.objects.get(id=self.kwargs["session_id"])

    def form_valid(self, form):
        session = form.save(commit=False)
        hall = session.hall
        start = session.start
        end = session.end
        overlapping_sessions = Sessions.objects.filter(
            hall=hall, start__lt=end, end__gt=start
        ).exclude(pk=session.id)
        if overlapping_sessions.exists():
            raise ValidationError(
                "Another session is already scheduled in this hall during this time."
            )
        self.session = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_session", kwargs={"id_session", self.session.id})


class CreateOrderDataView(IsLoging, FormView):
    template_name = "testapp/all_fields_form.html"
    form_class = OrderDataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["button_text"] = "Add order"
        return context

    def form_valid(self, form, **kwargs):
        form.instance.user = self.request.user
        form.instance.token = secrets.token_hex(16)
        comment = form.cleaned_data["comment"]
        if not comment:
            comment = None
        order_data = form.save()
        seat = get_object_or_404(Seats, id=self.kwargs["seat_id"])
        session = get_object_or_404(Sessions, id=self.kwargs["session_id"])
        self.reservation = Reservations.objects.create(
            order=order_data, seat=seat, session=session
        )
        return super().form_valid(form)

    def get_success_url(self):
        return _("details_reservations", kwargs={"reservation_id": self.reservation.id})


class ReservationDetailView(IsYourReservation, DetailView):
    model = Reservations
    template_name = "testapp/details_reservation.html"
    context_object_name = "reservation"

    def get_object(self, queryset=None):
        return self.model.objects.get(id=self.kwargs["reservation_id"])
