from django.contrib import admin
from .models.__init__ import *


class SlugInAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)


class AuthorSlugCodetrailerInAdmin(admin.ModelAdmin):
    readonly_fields = ("author_post", "slug", "trailers_youtube_code")

    def save_model(self, request, obj, form, change):
        if not obj.author_post_id:
            obj.author_post = request.user
        super().save_model(request, obj, form, change)


# register your models here

admin.site.register(Movie, AuthorSlugCodetrailerInAdmin)
admin.site.register(Languages)
admin.site.register(Production)
admin.site.register(Genre)
admin.site.register(Recommendations)
admin.site.register(SubscriptionToMovie)
admin.site.register(News, SlugInAdmin)
admin.site.register(NewsComment)
admin.site.register(Groups, SlugInAdmin)
admin.site.register(Posts, SlugInAdmin)
admin.site.register(PostComment)
admin.site.register(Comment)
admin.site.register(Chats, SlugInAdmin)
admin.site.register(PrivateMessages)
admin.site.register(SeatsTypes)
admin.site.register(Seats)
admin.site.register(Halls)
admin.site.register(Sessions)
admin.site.register(Banks)
admin.site.register(OrderData)
admin.site.register(Reservations)
admin.site.register(User)
admin.site.register(SubscriptionToUser)
admin.site.register(UsersBlacklists)
admin.site.register(Notification)
admin.site.register(Video)
