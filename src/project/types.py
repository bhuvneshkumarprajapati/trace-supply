from django.contrib.auth.models import User
from django.http import HttpRequest


class AuthedRequest(HttpRequest):
    """An HttpRequest whose user is guaranteed to be authenticated."""

    user: User  # type: ignore[assignment]
