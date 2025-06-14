import logging

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
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.auth.schemas import totp_schema
from apps.auth.serializers import RecoveryCodeVerifySerializer, TOTPCodeSerializer
from apps.auth.utils import get_jwt_tokens_for_user, get_session_mfa_user
from core.adapters import get_adapter

User = get_user_model()

logger = logging.getLogger(__name__)


@totp_schema
class TotpViewSet(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action in {"activate", "verify"}:
            return TOTPCodeSerializer
        elif self.action == "verify_recovery_code":
            return RecoveryCodeVerifySerializer
        return None

    def get_permissions(self):
        if self.action in {
            "status",
            "setup",
            "activate",
            "deactivate",
            "generate_recovery_codes",
            "recovery_codes",
        }:
            self.permission_classes = [IsAuthenticated]
        elif self.action in {
            "verify",
            "verify_recovery_code",
        }:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def status(self, request):
        """Check if TOTP is enabled for the user."""
        is_enabled = is_mfa_enabled(request.user)
        return Response(
            {"is_enabled": is_enabled},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def setup(self, request):
        """Set up TOTP for the user."""
        totp_secret = auth.generate_totp_secret()

        session_key = f"totp_secret_{request.user.id}"

        request.session[session_key] = totp_secret
        request.session.save()
        logger.info(
            "User session %s is setting up TOTP with secret: %s",
            request.session.get(session_key),
            totp_secret,
        )

        adapter = get_adapter(is_mfa=True)
        totp_uri = adapter.build_totp_url(request.user, totp_secret)
        qr_code_svg = adapter.build_totp_svg(totp_uri)

        return Response(
            {
                "secret": totp_secret,
                "qr_code": qr_code_svg,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def activate(self, request):
        """Activate TOTP for the user."""
        serializer = TOTPCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        totp_secret = request.session.get(f"totp_secret_{request.user.id}")
        logger.info(
            "User %s is activating TOTP with code: %s and secret: %s",
            request.user.id,
            code,
            totp_secret,
        )
        if not totp_secret:
            return Response(
                {"detail": _("TOTP is not set up for this user.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Checker than user can add a new authenticator
        try:
            validate_can_add_authenticator(request.user)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify the TOTP code
        adapter = get_adapter(is_mfa=True)
        if not adapter.verify_totp(totp_secret, code):
            return Response(
                {"error": "Invalid code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Activate TOTP code
        authenticator = Authenticator.objects.create(
            user=request.user,
            type=Authenticator.Type.TOTP,
            data={
                "secret": adapter.encrypt(totp_secret),
            },
        )
        authenticator.record_usage()

        # Delete the TOTP secret from the session
        if f"totp_setup_{request.user.id}" in request.session:
            del request.session[f"totp_setup_{request.user.id}"]
            request.session.save()

        # Generate recovery codes
        recovery_codes = generate_recovery_codes(request.user)

        return Response({
            "status": True,
            "recovery_codes": recovery_codes,
        })

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """Verify TOTP code."""
        serializer = TOTPCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # Get user from a session
        user = get_session_mfa_user(request)

        if not user:
            return Response(
                {"detail": _("First you need log in")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Checker than user can get an authenticator
        try:
            authenticator = Authenticator.objects.get(
                user=user, type=Authenticator.Type.TOTP
            )
        except Authenticator.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {"detail": _("Totp is not set up for this user.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        adapter = get_adapter(is_mfa=True)
        totp_secret = adapter.decrypt(authenticator.data["secret"])

        # Verify the TOTP code
        if not adapter.verify_totp(totp_secret, code):
            return Response(
                {"detail": _("Wrong code")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authenticator.record_usage()

        # Delete the TOTP secret from the session
        if "mfa_user_id" in request.session:
            del request.session["mfa_user_id"]
            request.session.save()

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

    @action(detail=False, methods=["post"])
    def deactivate(self, request):
        """Deactivate TOTP for user."""
        try:
            authenticator = Authenticator.objects.get(
                user=request.user, type=Authenticator.Type.TOTP
            )
        except Authenticator.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {"error": _("TOTP not activated for this user")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        adapter = get_adapter(is_mfa=True)
        if not adapter.can_delete_authenticator(authenticator):
            return Response(
                {"error": _("Cannot delete this authenticator")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authenticator.delete()
        delete_dangling_recovery_codes(request.user)
        return Response({"status": True})

    @action(detail=False, methods=["post"])
    def generate_recovery_codes(self, request):
        """Generate new recovery codes for the user."""
        if not is_mfa_enabled(request.user):
            return Response(
                {"error": _("MFA is not enabled for this user")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not can_generate_recovery_codes(request.user):
            return Response(
                {"error": _("User cannot generate recovery codes")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Delete existing recovery codes
            Authenticator.objects.filter(
                user=request.user, type=Authenticator.Type.RECOVERY_CODES
            ).delete()

            # Create new recovery codes
            rc_auth = RecoveryCodes.activate(request.user)

            # Downloading recovery codes
            recovery_codes = rc_auth.get_unused_codes()

            return Response(
                {"recovery_codes": recovery_codes},
                status=status.HTTP_201_CREATED,
            )

        except ReauthenticationRequired:
            return Response(
                {"error": "Reauthorization required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["get"])
    def recovery_codes(self, request):
        """View existing recovery codes for the user."""
        if not is_mfa_enabled(request.user):
            return Response(
                {"error": _("MFA is not enabled for this user")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authenticator = Authenticator.objects.filter(
            user=request.user,
            type=Authenticator.Type.RECOVERY_CODES,
        ).first()
        if not authenticator:
            return Response(
                {"error": _("No recovery codes found")},
                status=status.HTTP_404_NOT_FOUND,
            )

        recovery_codes = RecoveryCodes(authenticator)
        unused_codes = recovery_codes.get_unused_codes()
        return Response(
            {"recovery_codes": unused_codes},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def verify_recovery_code(self, request):
        """Verify a recovery code."""
        serializer = RecoveryCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recovery_code = serializer.validated_data["code"]

        user = get_session_mfa_user(request)
        if not user:
            return Response(
                {"detail": _("First you need log in")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            authenticator = Authenticator.objects.get(
                user=request.user, type=Authenticator.Type.RECOVERY_CODES
            )
        except Authenticator.DoesNotExist:  # type: ignore[attr-defined]
            return Response(
                {"error": _("No recovery codes found")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create recovery codes
        recovery_codes = RecoveryCodes(authenticator)

        # Validate the code
        if recovery_codes.validate_code(recovery_code):
            authenticator.record_usage()

            # clear session for mfa user
            if "mfa_user_id" in request.session:
                del request.session["mfa_user_id"]
                request.session.save()

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
        else:
            return Response(
                {"error": _("Wrong code")},
                status=status.HTTP_400_BAD_REQUEST,
            )
