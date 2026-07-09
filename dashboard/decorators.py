from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages


def owner_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect("accounts:login")

        if request.user.is_superuser:

            return view_func(request, *args, **kwargs)

        if request.user.role == "owner":

            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "You don't have permission to access this page.",
        )

        return redirect("home")

    return wrapper