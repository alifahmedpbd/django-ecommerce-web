from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from user_agents import parse


class UserActivityMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            ua_string = request.META.get(
                "HTTP_USER_AGENT",
                "",
            )

            ua = parse(ua_string)

            user_agent = ua_string.lower()

            # ==========================================
            # Device
            # ==========================================

            if ua.is_mobile:

                device = "📱 Mobile"

            elif ua.is_tablet:

                device = "📲 Tablet"

            elif ua.is_pc:

                device = "💻 Desktop"

            else:

                device = "🖥 Unknown"

            # ==========================================
            # Browser
            # ==========================================

            if "edg" in user_agent:

                browser = "🌐 Microsoft Edge"

            elif "opr" in user_agent or "opera" in user_agent:

                browser = "🌐 Opera"

            elif "chrome" in user_agent and "edg" not in user_agent:

                browser = "🌐 Google Chrome"

            elif "firefox" in user_agent:

                browser = "🌐 Mozilla Firefox"

            elif "safari" in user_agent and "chrome" not in user_agent:

                browser = "🌐 Safari"

            else:

                browser = f"🌐 {ua.browser.family}"

            if ua.browser.version_string:

                browser += f" {ua.browser.version_string}"

            # ==========================================
            # Operating System
            # ==========================================

            os_name = ua.os.family

            if ua.os.version_string:

                os_name += f" {ua.os.version_string}"

            # ==========================================
            # Save Activity
            # ==========================================

            request.user.last_activity = timezone.now()

            request.user.last_seen_page = request.path

            request.user.last_ip = self.get_client_ip(request)

            request.user.browser = browser

            request.user.device = device

            request.user.operating_system = os_name

            request.user.save(
                update_fields=[
                    "last_activity",
                    "last_seen_page",
                    "last_ip",
                    "browser",
                    "device",
                    "operating_system",
                ]
            )

        return self.get_response(request)

    def get_client_ip(self, request):

        x_forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if x_forwarded_for:

            return x_forwarded_for.split(",")[0].strip()

        return request.META.get(
            "REMOTE_ADDR",
            "",
        )


class BlockedUserMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            if request.user.is_blocked:

                allowed = [

                    "/accounts/logout/",
                    "/admin/",

                ]

                if not any(
                    request.path.startswith(path)
                    for path in allowed
                ):

                    messages.error(
                        request,
                        "Your account has been blocked."
                    )

                    return redirect(
                        "accounts:logout"
                    )

        return self.get_response(request)