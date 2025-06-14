import logging

from allauth.account.models import EmailAddress
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.auth.schemas import auth_schema
from apps.auth.serializers import (
    CheckEmailSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResendEmailSerializer,
    VerifyEmailSerializer,
)
from apps.auth.utils import get_jwt_tokens_for_user

User = get_user_model()

logger = logging.getLogger(__name__)


@auth_schema
class AuthViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        elif self.action == "register":
            return RegisterSerializer
        elif self.action == "refresh":
            return RefreshTokenSerializer
        elif self.action == "resend_email":
            return ResendEmailSerializer
        elif self.action == "verify_email":
            return VerifyEmailSerializer
        elif self.action == "check_email":
            return CheckEmailSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in {
            "login",
            "register",
            "refresh",
            "resend_email",
            "verify_email",
            "check_email",
        }:
            self.permission_classes = [AllowAny]
        elif self.action in {
            "logout",
        }:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(methods=["post"], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"detail": _("Wrong login credentials. Please try again.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": _("Account is inactive")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if is_mfa_enabled(user):
            request.session["mfa_user_id"] = user.id
            request.session.save()
            return Response(
                {"mfa_required": True},
                status=status.HTTP_200_OK,
            )

        access, refresh = get_jwt_tokens_for_user(user)
        return Response({
            "access": access,
            "refresh": refresh,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
        })

    @action(methods=["post"], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request=request)
        return Response(
            {"detail": _(f"Verification email will be send to: {user.email}")},
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["get"], detail=False, url_path="verify_email/(?P<key>[^/.]+)")
    def verify_email(self, request, key=None):
        logger.info("Processing email verification for key: %s", key)
        serializer = self.get_serializer(data={"key": key})
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request=request)
        return Response(
            {
                "detail": _(
                    f"Email {user.email} was verified successfully. You can now login."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False)
    def check_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            email_address = EmailAddress.objects.get(
                email=serializer.validated_data.get("email"),
                verified=True,
            )
            if email_address.verified:
                return Response(
                    {
                        "detail": [
                            _(f"Email {email_address.email} was verified successfully.")
                        ]
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"errors": [_("Email {email_address.email} is not verified.")]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmailAddress.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {
                    "errors": [
                        _("Email address not found for this user. Please try again.")
                    ]
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(methods=["post"], detail=False)
    def resend_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"detail": _(f"Verify email sent to: {user.email}")},
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["post"], detail=False)
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False)
    def logout(self, request):
        request.session.flush()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
