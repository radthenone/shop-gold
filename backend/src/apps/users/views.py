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


class AccountViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(
        methods=["post"],
        detail=False,
        description="Register a new user",
        url_path="register",
        url_name="register",
    )
    def register(self, request):
        """
        Register a new user
        """
        serializer = RegisterSerializer(data=request.data)
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
        methods=["get", "post"],
        detail=False,
        description="Verify email",
        url_path="verify-email",
        url_name="verify-email",
    )
    def verify_email(self, request):
        """
        Verify email
        """
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            code = serializer.validated_data["code"]
            if not code:
                return Response(
                    {"error": "Code is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                email_confirmation = EmailConfirmationHMAC.from_key(code)
                if not email_confirmation:
                    return Response(
                        {"error": "Invalid code"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                adapter = AccountAdapter()
                adapter.confirm_email(request, email_confirmation.email_address)
                return Response(
                    {"detail": "Email verified successfully"},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=False,
        methods=["post"],
        description="Resend email",
        url_path="resend-email",
        url_name="resend-email",
    )
    def resend_email(self, request):
        """
        Resend email
        """
        serializer = ResendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            email_address = EmailAddress.objects.get(email=email, verified=False)

            adapter = AccountAdapter()
            adapter.send_confirmation_mail(request, email_address, signup=False)

            return Response(
                {"message": "Verification email resent successfully"},
                status=status.HTTP_200_OK,
            )
        except EmailAddress.DoesNotExist:
            return Response(
                {"error": "No unverified email found for this address"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to resend email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
