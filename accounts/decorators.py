from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages


def owner_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if (
            request.user.is_authenticated
            and request.user.role == "owner"
        ):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "You are not authorized to access this page."
        )

        return redirect("home")

    return wrapper


def staff_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if (
            request.user.is_authenticated
            and request.user.role == "staff"
        ):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "You are not authorized to access this page."
        )

        return redirect("home")

    return wrapper


def owner_or_staff_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if (
            request.user.is_authenticated
            and request.user.role in ["owner", "staff"]
        ):
            return view_func(request, *args, **kwargs)

        messages.error(
            request,
            "You are not authorized to access this page."
        )

        return redirect("home")

    return wrapper