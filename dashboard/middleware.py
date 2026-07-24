from django.shortcuts import render
from dashboard.helpers import feature_enabled


class MaintenanceModeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if feature_enabled("maintenance"):

            # Admin/Login/Static/Media সবসময় Allow
            allowed_paths = [
                "/admin/",
                "/accounts/login/",
                "/accounts/logout/",
                "/static/",
                "/media/",
            ]

            if any(request.path.startswith(path) for path in allowed_paths):
                return self.get_response(request)

            # Staff/Superuser সবসময় Allow
            if (
                request.user.is_authenticated
                and (
                    request.user.is_staff
                    or request.user.is_superuser
                )
            ):
                return self.get_response(request)

            # বাকি সবাই Maintenance Page দেখবে
            return render(request, "maintenance.html")

        return self.get_response(request)
    
class ComingSoonMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if feature_enabled("coming_soon"):

            allowed_paths = [
                "/admin/",
                "/accounts/login/",
                "/accounts/logout/",
                "/static/",
                "/media/",
            ]

            if any(request.path.startswith(path) for path in allowed_paths):
                return self.get_response(request)

            if (
                request.user.is_authenticated
                and (
                    request.user.is_staff
                    or request.user.is_superuser
                )
            ):
                return self.get_response(request)

            return render(
                request,
                "coming_soon.html",
            )

        return self.get_response(request)