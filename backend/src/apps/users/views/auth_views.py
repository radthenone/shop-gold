from typing import TYPE_CHECKING

from allauth.account.models import EmailAddress
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.schemas import auth_schema
from apps.users.serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResendEmailSerializer,
    VerifyEmailSerializer,
)
from apps.users.utils import get_jwt_tokens_for_user

if TYPE_CHECKING:
    from apps.users.models import User


@auth_schema
class AccountViewSet(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action == "login":
            return LoginSerializer
        elif self.action == "refresh":
            return RefreshTokenSerializer
        elif self.action == "resend_email":
            return ResendEmailSerializer
        elif self.action == "verify_email":
            return VerifyEmailSerializer
        return RegisterSerializer

    def get_object(self):
        """
        Get the user object from the request
        """
        if self.action == "check_email":
            try:
                return EmailAddress.objects.get(user=self.request.user)
            except EmailAddress.DoesNotExist:
                return None

    @action(
        methods=["post"],
        detail=False,
        description="Register a new user",
        url_path="register",
        url_name="register",
        permission_classes=[AllowAny],
    )
    def register(self, request):
        """
        Register a new user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request)
        return Response(
            {"detail": f"Verification email sent to {user.email}"},
            status=status.HTTP_201_CREATED,
        )

    @action(
        methods=["get"],
        detail=False,
        description="Verify email",
        url_path="verify-email/(?P<key>[^/.]+)",
        url_name="verify-email",
        permission_classes=[AllowAny],
    )
    def verify_email(self, request, key=None):
        """
        Verify email
        """
        serializer = self.get_serializer(data={"key": key})
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request)
        return Response(
            {"detail": f"Email {user.email} verified successfully"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        description="Check email",
        url_path="check-email",
        url_name="check-email",
        permission_classes=[IsAuthenticated],
    )
    def check_email(self, request):
        email_address = self.get_object()
        if email_address.verified:
            return Response(
                {"detail": f"Email {email_address.email} is verified"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": f"Email {email_address.email} is not verified"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=["post"],
        description="Resend email",
        url_path="resend-email",
        url_name="resend-email",
        permission_classes=[AllowAny],
    )
    def resend_email(self, request):
        """
        Resend email
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request)
        return Response(
            {"detail": f"Verification email re-sent to {user.email}"},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        description="Login",
        url_path="login",
        url_name="login",
        permission_classes=[AllowAny],
    )
    def login(self, request):
        """
        Login
        """
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user: User | None = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"detail": "Invalid login credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Account is inactive"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if is_mfa_enabled(user):
            # Zapisz identyfikator użytkownika w sesji do weryfikacji MFA
            request.session["mfa_login"] = user.id
            request.session.save()
            return Response({"mfa_required": True}, status=status.HTTP_200_OK)

        access, refresh = get_jwt_tokens_for_user(user)
        return Response(
            {
                "access": access,
                "refresh": refresh,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        description="Logout",
        url_path="logout",
        url_name="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request):
        """
        Wylogowanie użytkownika i usunięcie sesji
        """
        # Usuń wszystkie dane sesji, w tym flagi MFA
        request.session.flush()
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        description="Refresh JWT token",
        url_path="refresh",
        url_name="refresh",
        permission_classes=[AllowAny],
    )
    def refresh(self, request):
        """
        Refresh JWT token
        """
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
