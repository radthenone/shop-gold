from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def get_jwt_tokens_for_user(user: User) -> tuple[str, str]:
    """
    Generate JWT tokens for the given user.
    """
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    return access, str(refresh)


def get_session_mfa_user(request: Request) -> User | None:
    user_id = request.session.get("mfa_user_id")
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None
