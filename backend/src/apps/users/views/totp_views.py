import json
import logging
from datetime import datetime

from allauth.core.exceptions import ReauthenticationRequired
from allauth.mfa.base.internal.flows import delete_dangling_recovery_codes
from allauth.mfa.internal.flows.add import validate_can_add_authenticator
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.recovery_codes.internal.flows import (
    can_generate_recovery_codes,
    generate_recovery_codes,
)
from allauth.mfa.totp.internal import auth
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import (
    RecoveryCodesSerializer,
    RecoveryCodeVerifySerializer,
    TOTPCodeSerializer,
    TOTPSetupSerializer,
    TOTPStatusResponseSerializer,
    TOTPStatusSerializer,
)
from apps.users.utils import get_jwt_tokens_for_user
from core.adapters import get_adapter

User = get_user_model()

logger = logging.getLogger(__name__)


@extend_schema_view(
    status=extend_schema(
        tags=["TOTP"],
        responses={
            200: TOTPStatusSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    setup=extend_schema(
        tags=["TOTP"],
        request=None,
        responses={
            200: TOTPSetupSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    activate=extend_schema(
        tags=["TOTP"],
        request=TOTPCodeSerializer,
        responses={
            200: TOTPStatusResponseSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    verify=extend_schema(
        tags=["TOTP"],
        request=TOTPCodeSerializer,
        responses={
            200: TOTPStatusResponseSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    deactivate=extend_schema(
        tags=["TOTP"],
        responses={
            200: TOTPStatusResponseSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    generate_recovery_codes=extend_schema(
        tags=["TOTP"],
        responses={
            200: RecoveryCodesSerializer,
            400: TOTPStatusResponseSerializer,
        },
    ),
    recovery_codes=extend_schema(
        tags=["TOTP"],
        responses={
            200: RecoveryCodesSerializer,
            400: TOTPStatusResponseSerializer,
            404: TOTPStatusResponseSerializer,
        },
    ),
    verify_recovery_code=extend_schema(
        tags=["TOTP"],
        request=RecoveryCodeVerifySerializer,
        responses={
            200: TOTPStatusResponseSerializer,
            400: TOTPStatusResponseSerializer,
            404: TOTPStatusResponseSerializer,
        },
    ),
)
class TOTPViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def status(self, request):
        """Check if TOTP is enabled for the user."""

        is_enabled = is_mfa_enabled(request.user)
        return Response({"is_enabled": is_enabled})

    @action(detail=False, methods=["post"])
    def setup(self, request):
        """Set up TOTP for the user."""

        # Generate a new TOTP secret and store it in the cache
        secret = auth.generate_totp_secret()
        # cache.set(f"totp_setup_{request.user.id}", secret)

        request.session[f"totp_setup_{request.user.id}"] = secret

        request.session.save()
        # Logowanie informacji o konfiguracji TOTP
        logger.info(
            f"Setup: user={request.user.id}, "
            f"session_key={request.session.session_key}, "
            f"secret={secret}"
        )

        # Generate QR code URL
        adapter = get_adapter(is_mfa=True)
        totp_uri = adapter.build_totp_url(request.user, secret)
        qr_code_svg = adapter.build_totp_svg(totp_uri)

        return Response({"qr_code_svg": qr_code_svg})

    @action(detail=False, methods=["post"])
    def activate(self, request):
        """Activate TOTP for the user."""

        serializer = TOTPCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Get the TOTP secret from the cache
        # secret = cache.get(f"totp_setup_{request.user.id}")
        secret = request.session.get(f"totp_setup_{request.user.id}", None)

        print(
            f"Activate: user={request.user.id}, "
            f"session_key={request.session.session_key}, "
            f"secret={secret}, code={code}"
        )
        if secret is None:
            return Response(
                {"error": "Setup not initiated"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Checker than user can add a new authenticator
        try:
            validate_can_add_authenticator(request.user)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the TOTP code
        adapter = get_adapter(is_mfa=True)
        if not adapter.verify_totp(secret, code):
            return Response(
                {"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Activate TOTP code
        authenticator = Authenticator.objects.create(
            user=request.user,
            type=Authenticator.Type.TOTP,
            data={
                "secret": adapter.encrypt(secret),
            },
        )
        authenticator.record_usage()

        # Delete the TOTP secret from the cache
        # cache.delete(f"totp_setup_{request.user.id}")
        del request.session[f"totp_setup_{request.user.id}"]

        # Generate recovery codes
        recovery_codes = generate_recovery_codes(request.user)

        return Response({
            "status": "TOTP activated",
            "recovery_codes": recovery_codes,
        })

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def verify(self, request):
        """Verify TOTP code for the user."""
        # Validate input data
        serializer = TOTPCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Determine user: for MFA during login from mfa_login session
        mfa_id = request.session.get("mfa_login")
        if mfa_id:
            try:
                user = User.objects.get(id=mfa_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid user session"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user = request.user

        # Check attempt limits
        attempts = cache.get(f"totp_attempts_{user.id}", 0)
        if attempts >= 3:
            return Response(
                {"error": "Too many attempts. Try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify TOTP code
        code = serializer.validated_data["code"]
        try:
            authenticator = Authenticator.objects.get(
                user=user, type=Authenticator.Type.TOTP
            )
        except Authenticator.DoesNotExist:
            return Response(
                {"error": "TOTP not enabled"}, status=status.HTTP_400_BAD_REQUEST
            )

        totp = auth.TOTP(authenticator)
        if not totp.validate_code(code):
            # Increase attempt counter
            cache.set(
                f"totp_attempts_{user.id}", attempts + 1, timeout=300
            )  # 5 minutes
            return Response(
                {"error": "Invalid code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset attempt counter after successful verification
        cache.delete(f"totp_attempts_{user.id}")

        # Set session start time
        cache.set(
            f"totp_session_start_{user.id}", datetime.now().timestamp(), timeout=300
        )

        # Mark session as verified
        request.session[f"totp_verified_{user.id}"] = json.dumps({"verified": True})

        # If this is MFA during login, complete the login process
        if request.session.get("mfa_login"):
            del request.session["mfa_login"]
            tokens = get_jwt_tokens_for_user(user)
            return Response(
                {
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "role": user.role,
                    },
                },
                status=status.HTTP_200_OK,
            )

        # For regular TOTP verification (not during login)
        return Response({"status": "Verified"})

    @action(detail=False, methods=["post"])
    def deactivate(self, request):
        """Deactivate TOTP for user."""
        try:
            authenticator = Authenticator.objects.get(
                user=request.user, type=Authenticator.Type.TOTP
            )
        except Authenticator.DoesNotExist:
            return Response(
                {"error": "TOTP not activated for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        adapter = get_adapter(is_mfa=True)
        if not adapter.can_delete_authenticator(authenticator):
            return Response(
                {"error": "Cannot delete this authenticator"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authenticator.delete()
        delete_dangling_recovery_codes(request.user)
        return Response({"status": "TOTP deactivated successfully"})

    @extend_schema(
        responses={200: RecoveryCodesSerializer, 400: TOTPStatusResponseSerializer},
        description="Generate new recovery codes for user.",
        tags=["TOTP"],
    )
    @action(detail=False, methods=["post"])
    def generate_recovery_codes(self, request):
        """Generate new recovery codes for user."""
        if not is_mfa_enabled(request.user):
            return Response(
                {"error": "MFA is not enabled for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not can_generate_recovery_codes(request.user):
            return Response(
                {"error": "User cannot generate recovery codes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Usuń istniejące kody odzyskiwania
            Authenticator.objects.filter(
                user=request.user, type=Authenticator.Type.RECOVERY_CODES
            ).delete()

            # Utwórz nowe kody odzyskiwania
            rc_auth = RecoveryCodes.activate(request.user)

            # Pobierz niewykorzystane kody
            recovery_codes = rc_auth.get_unused_codes()

            return Response({"recovery_codes": recovery_codes})

        except ReauthenticationRequired:
            return Response(
                {"error": "Reauthorization required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @extend_schema(
        responses={200: RecoveryCodesSerializer, 400: TOTPStatusResponseSerializer},
        description="View existing recovery codes for user.",
        tags=["TOTP"],
    )
    @action(detail=False, methods=["get"])
    def recovery_codes(self, request):
        """View existing recovery codes for user."""
        if not is_mfa_enabled(request.user):
            return Response(
                {"error": "MFA is not enabled for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authenticator = Authenticator.objects.filter(
            user=request.user,
            type=Authenticator.Type.RECOVERY_CODES,
        ).first()
        if not authenticator:
            return Response(
                {"error": "No recovery codes found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        recovery_codes = RecoveryCodes(authenticator)
        unused_codes = recovery_codes.get_unused_codes()
        return Response({"recovery_codes": unused_codes})

    @extend_schema(
        request=RecoveryCodeVerifySerializer,
        responses={
            200: TOTPStatusResponseSerializer,
            400: TOTPStatusResponseSerializer,
        },
        description="Verify a recovery code.",
        tags=["TOTP"],
    )
    @action(detail=False, methods=["post"])
    def verify_recovery_code(self, request):
        """Verify a recovery code."""
        serializer = RecoveryCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        try:
            authenticator = Authenticator.objects.get(
                user=request.user, type=Authenticator.Type.RECOVERY_CODES
            )
        except Authenticator.DoesNotExist:
            return Response(
                {"error": "No recovery codes found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create RecoveryCodes instance
        recovery_codes = RecoveryCodes(authenticator)

        # Validate the code
        if recovery_codes.validate_code(code):
            # Set the session as verified
            request.session[f"totp_verified_{request.user.id}"] = json.dumps({
                "verified": True
            })
            return Response({"status": "Recovery code verified"})
        else:
            return Response(
                {"error": "Invalid recovery code"},
                status=status.HTTP_400_BAD_REQUEST,
            )
