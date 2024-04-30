from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import get_object_or_404

from .models import Reservations


class IsLoging(LoginRequiredMixin):
    pass


class IsAdmin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff and request.user.is_superuser):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IsYourReservation(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user
            == get_object_or_404(Reservations, id=kwargs["reservation_id"]).order.user
        ):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
