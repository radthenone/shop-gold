from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import complete_signup, setup_user_email
from allauth.account.views import ConfirmEmailView
from allauth.mfa.base.forms import AuthenticateForm
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.forms import ActivateTOTPForm, DeactivateTOTPForm
from dj_rest_auth.registration.views import RegisterView
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.adapters import AccountAdapter
from apps.users.serializers import (
    RegisterSerializer,
    ResendEmailSerializer,
    VerifyEmailSerializer,
)

User = get_user_model()


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    @action(
        methods=["post"],
        detail=False,
        description="Register a new user",
        url_path="register",
        url_name="register",
        serializer_class=RegisterSerializer,
    )
    def register(self, request):
        """
        Register a new user
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save(request)
            return Response(
                {"detail": f"Verification email sent to {user.email}"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["post"],
        detail=False,
        description="Verify email",
        url_path="verify-email",
        url_name="verify-email",
        serializer_class=VerifyEmailSerializer,
    )
    def verify_email(self, request):
        """
        Verify email
        """
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
            },
        )
        if serializer.is_valid(raise_exception=True):
            user = serializer.save(request)
            return Response(
                {"detail": f"Email verified successfully for {user.email}"},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["post"],
        description="Resend email",
        url_path="resend-email",
        url_name="resend-email",
        serializer_class=ResendEmailSerializer,
    )
    def resend_email(self, request):
        """
        Resend email
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save(request)
            return Response(
                {"detail": f"Verification email re-sent to {user.email}"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
