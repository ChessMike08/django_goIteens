from django.utils import timezone


class OnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_user = request.user
        if request.user.is_authenticated:
            now = timezone.now()
            current_user.last_action = now
            current_user.save()
        response = self.get_response(request)
        return response
