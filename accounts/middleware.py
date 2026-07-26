from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from user_agents import parse

UPDATE_INTERVAL = 60  # seconds


class UserActivityMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if not request.user.is_authenticated:

            return response

        # Skip static/media/admin requests
        ignored_paths = (
            "/static/",
            "/media/",
            "/favicon.ico",
            "/admin/js/",
            "/admin/css/",
        )

        if request.path.startswith(ignored_paths):

            return response

        now = timezone.now()

        user = request.user

        # Update only every 60 seconds
        if user.last_activity:

            seconds = (now - user.last_activity).total_seconds()

            if seconds < UPDATE_INTERVAL:

                return response

        ua_string = request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

        ua = parse(ua_string)

        user_agent = ua_string.lower()

        # ==========================
        # Device
        # ==========================

        if ua.is_mobile:

            device = "📱 Mobile"

        elif ua.is_tablet:

            device = "📲 Tablet"

        elif ua.is_pc:

            device = "💻 Desktop"

        else:

            device = "🖥 Unknown"

        # ==========================
        # Browser
        # ==========================

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

        # ==========================
        # Operating System
        # ==========================

        os_name = ua.os.family

        if ua.os.version_string:

            os_name += f" {ua.os.version_string}"

        # ==========================
        # IP
        # ==========================

        ip = self.get_client_ip(request)

        changed_fields = []

        user.last_activity = now
        changed_fields.append("last_activity")

        if user.last_seen_page != request.path:

            user.last_seen_page = request.path
            changed_fields.append("last_seen_page")

        if user.last_ip != ip:

            user.last_ip = ip
            changed_fields.append("last_ip")

        if user.browser != browser:

            user.browser = browser
            changed_fields.append("browser")

        if user.device != device:

            user.device = device
            changed_fields.append("device")

        if user.operating_system != os_name:

            user.operating_system = os_name
            changed_fields.append("operating_system")

        if changed_fields:

            user.save(
                update_fields=changed_fields,
            )

        return response

    def get_client_ip(self, request):

        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded:

            return forwarded.split(",")[0].strip()

        return request.META.get(
            "REMOTE_ADDR",
            "",
        )


class BlockedUserMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.is_blocked:

            allowed = (
                "/accounts/logout/",
                "/admin/",
            )

            if not request.path.startswith(allowed):

                messages.error(
                    request,
                    "Your account has been blocked.",
                )

                return redirect(
                    "accounts:logout",
                )

        return self.get_response(request)