from django.db.utils import DatabaseError, OperationalError, ProgrammingError

from .models import Wishlist


def wishlist_count(request):
    # FIXED: Prevent a database or migration issue from crashing every request
    # when the wishlist table is unavailable during deployment or startup.
    count = 0

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        try:
            count = Wishlist.objects.filter(user=user).count()
        except (DatabaseError, OperationalError, ProgrammingError):
            count = 0

    return {
        "wishlist_count": count,
    }