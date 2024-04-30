from django.urls import path
from .views import *

urlpatterns = [
    path("", MainView.as_view(), name="main_page"),
    path("accounts/signup/", SignupView.as_view(), name="signup"),
    path("accounts/login/", AuthenticationView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("my_profile/", my_profile_redirect, name="my_profile"),
    path("profile/@/<slug:slug>/", ProfileView.as_view(), name="profile"),
    path(
        "subscription/user/@/<slug:slug>/",
        CreateSubscriptionToUserView.as_view(),
        name="subscription_to_user",
    ),
    path(
        "unsubscription/user/<int:subscription_to_user_id>/",
        DeleteSubscriptionToUserView.as_view(),
        name="unsubscription_to_user",
    ),
    path(
        "create/user/blacklist/<slug:slug>/",
        CreateUserToBlacklistView.as_view(),
        name="create_user_to_blacklist",
    ),
    path(
        "delete/user/blacklist/<slug:slug>/",
        DeleteUserToBlacklistView.as_view(),
        name="delete_user_to_blacklist",
    ),
    path("my_profile/edit/", EditProfileView.as_view(), name="edit_profile"),
    path(
        "my_profile/password_change/",
        PasswordChangeCustomView.as_view(),
        name="password_change",
    ),
    path("add/movie/", MovieFormView.as_view(), name="movie_add"),
    path(
        "add/recommendation/",
        AddRecommendationView.as_view(),
        name="add_recommendation",
    ),
    path(
        "delete/recommendation/<int:recommendation_id>/",
        DeleteRecommendationView.as_view(),
        name="delete_recommendation",
    ),
    path(
        "subscription/movie/<slug:movie_slug>/",
        CreateSubscriptionToMovieView.as_view(),
        name="subscription_to_movie",
    ),
    path(
        "unsubscription/movie/<int:subscription_to_movie_id>",
        DeleteSubscriptionToMovieView.as_view(),
        name="unsubscription_to_movie",
    ),
    path(
        "add/production/api/",
        ProductionFormAPIView.as_view(),
        name="production_add_api",
    ),
    path("add/language/api/", LanguageFormAPIView.as_view(), name="language_add_api"),
    path("add/genre/", GenreFormView.as_view(), name="genre_add"),
    path("add/hall/", HallFormView.as_view(), name="hall_add"),
    path("add/movie/<slug:slug>/video/", VideoFormView.as_view(), name="video_add"),
    path("edit/movie/<slug:slug>/", MovieUpdateView.as_view(), name="edit_movie"),
    path("details/movie/<slug:slug>/", MovieDetailView.as_view(), name="details_movie"),
    path(
        "add/comment/movie/<slug:movie_slug>/",
        AddCommentView.as_view(),
        name="add_movie_comment",
    ),
    path("add/seats_type/", SeatsTypeFormView.as_view(), name="seats_type_add"),
    path("add/bank/", BankFormView.as_view(), name="bank_add"),
    path("add/news/", NewsFormView.as_view(), name="news_add"),
    path("details/news/<slug:slug>/", NewsDetailsView.as_view(), name="details_news"),
    path("edit/news/<slug:slug>/", NewsUpdateView.as_view(), name="edit_news"),
    path(
        "add/comment/news/<slug:news_slug>",
        AddNewsCommentView.as_view(),
        name="add_news_comment",
    ),
    path(
        "add/hall/<int:hall_id>/seat/",
        AddHallSeatView.as_view(),
        name="add_or_change_hall_seat",
    ),
    path("edit/seat/<int:seat_id>/", UpdateHallSeatView.as_view(), name="edit_seat"),
    path("delete/seat/<int:seat_id>", DeleteHallSeatView.as_view(), name="delete_seat"),
    path("add/session/", AddSessionView.as_view(), name="session_add"),
    path(
        "add/comment/session/<int:session_id>/",
        AddCommentView.as_view(),
        name="add_session_comment",
    ),
    path(
        "details/session/<int:session_id>",
        SessionDetailView.as_view(),
        name="details_session",
    ),
    path(
        "edit/session/<int:session_id>",
        UpdateSessionView.as_view(),
        name="edit_session",
    ),
    path(
        "add/order/<int:seat_id>/<int:hall_id>/<int:session_id>/",
        CreateOrderDataView.as_view(),
        name="order_add",
    ),
    path(
        "details/reservation/<int:reservation_id>",
        ReservationDetailView.as_view(),
        name="details_reservations",
    ),
]
