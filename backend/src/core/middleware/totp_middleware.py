import json

from allauth.mfa.utils import is_mfa_enabled
from django.http import JsonResponse
from rest_framework import status


class TOTPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for TOTP verification endpoints
        if request.path.startswith("/api/users/totp/verify/"):
            return self.get_response(request)

        # Skip if user is in MFA login process
        if request.session.get("mfa_login"):
            return self.get_response(request)

        # Check if user is authenticated and has MFA enabled
        if request.user.is_authenticated and is_mfa_enabled(request.user):
            # Check if TOTP is verified in session
            totp_verified = request.session.get(f"totp_verified_{request.user.id}")
            if not totp_verified:
                return JsonResponse(
                    {
                        "error": "MFA_SESSION_NEEDED",
                        "message": "MFA_REQUIRED",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # If stored as JSON string, parse it
            if isinstance(totp_verified, str):
                try:
                    verified_data = json.loads(totp_verified)
                    if not verified_data.get("verified", False):
                        return JsonResponse(
                            {
                                "error": "MFA_SESSION_NEEDED",
                                "message": "MFA_REQUIRED",
                            },
                            status=status.HTTP_403_FORBIDDEN,
                        )
                except json.JSONDecodeError:
                    # If can't parse JSON, consider not verified
                    return JsonResponse(
                        {
                            "error": "MFA_SESSION_NEEDED",
                            "message": "MFA_REQUIRED",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        # In all other cases, allow the request to proceed
        return self.get_response(request)
