from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiRequest,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

auth_schema = extend_schema_view(
    verify_email=extend_schema(
        tags=["Auth"],
        parameters=[
            OpenApiParameter(
                name="key",
                location="path",
                required=True,
                type=str,
                description="Verity key to e-mail",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "VerifyEmailResponse",
                    {
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "VerifyEmailResponse",
                        value={"detail": "Email {user.email} is verified"},
                    )
                ],
            ),
        },
    ),
    register=extend_schema(
        tags=["Auth"],
        request=OpenApiRequest(
            request=inline_serializer(
                "RegisterRequest",
                {
                    "username": serializers.CharField(),
                    "email": serializers.EmailField(),
                    "password": serializers.CharField(),
                    "rewrite_password": serializers.CharField(),
                    "first_name": serializers.CharField(),
                    "last_name": serializers.CharField(),
                },
            ),
            examples=[
                OpenApiExample(
                    "RegisterRequest",
                    value={
                        "username": "example_user",
                        "email": "user@example.com",
                        "password": "Password12345!",
                        "rewrite_password": "Password12345!",
                    },
                ),
            ],
        ),
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    "RegisterResponse",
                    {
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "RegisterResponse",
                        value={"detail": "Verification email sent to {user.email}"},
                    )
                ],
            ),
        },
    ),
    resend_email=extend_schema(
        tags=["Auth"],
        request=OpenApiRequest(
            request=inline_serializer(
                "ResendEmailRequest",
                {
                    "email": serializers.EmailField(),
                },
            ),
            examples=[
                OpenApiExample(
                    "ResendEmailRequest",
                    value={
                        "email": "user@example.com",
                    },
                ),
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "ResendEmailResponse",
                    {
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "ResendEmailResponse",
                        value={"detail": "Verification email resent to {user.email}"},
                    )
                ],
            ),
        },
    ),
    login=extend_schema(
        tags=["Auth"],
        request=OpenApiRequest(
            request=inline_serializer(
                "LoginRequest",
                {
                    "email": serializers.EmailField(),
                    "password": serializers.CharField(),
                },
            ),
            examples=[
                OpenApiExample(
                    "LoginRequest",
                    value={"email": "user@example.com", "password": "Password12345!"},
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "LoginResponse",
                    {
                        "mfa_required": serializers.BooleanField(default=False),
                        "access": serializers.CharField(),
                        "refresh": serializers.CharField(),
                        "user": inline_serializer(
                            "UserResponse",
                            {
                                "id": serializers.UUIDField(),
                                "email": serializers.EmailField(),
                                "username": serializers.CharField(),
                                "role": serializers.ChoiceField(
                                    choices=[
                                        ("customer", "Customer"),
                                        ("admin", "Admin"),
                                    ]
                                ),
                            },
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "LoginResponse",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "user": {
                                "id": "973e1d8b-299b-4ef2-941e-82015...",
                                "email": "user@example.com",
                                "username": "example_user",
                                "role": "customer",
                            },
                        },
                    ),
                    OpenApiExample(
                        "LoginMfaResponse",
                        value={
                            "mfa_required": True,
                        },
                    ),
                ],
            ),
        },
    ),
    refresh=extend_schema(
        tags=["Auth"],
        request=OpenApiRequest(
            request=inline_serializer(
                "RefreshTokenRequest",
                {
                    "refresh": serializers.CharField(),
                },
            ),
            examples=[
                OpenApiExample(
                    "RefreshTokenRequest",
                    value={
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    },
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "RefreshTokenResponse",
                    {
                        "access": serializers.CharField(),
                        "refresh": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "RefreshTokenResponse",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        },
                    )
                ],
            ),
        },
    ),
    check_email=extend_schema(
        tags=["Auth"],
        request=OpenApiRequest(
            request=inline_serializer(
                "CheckEmailRequest",
                {
                    "email": serializers.EmailField(),
                },
            ),
            examples=[
                OpenApiExample(
                    "CheckEmailRequest",
                    value={"email": "user@example.com"},
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "CheckEmailResponse",
                    {
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "CheckEmailResponse",
                        value={"detail": "Email {email_address.email} is verified"},
                    )
                ],
            ),
        },
    ),
    logout=extend_schema(
        tags=["Auth"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "LogoutResponse",
                    {
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "LogoutResponse",
                        value={"detail": "Successfully logged out"},
                    )
                ],
            ),
        },
    ),
)


totp_schema = extend_schema_view(
    status=extend_schema(
        tags=["Totp"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpResponse",
                    {
                        "is_enabled": serializers.BooleanField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpResponse",
                        value={"is_enabled": True},
                    ),
                    OpenApiExample(
                        "TotpResponse",
                        value={"is_enabled": False},
                    ),
                ],
            )
        },
    ),
    setup=extend_schema(
        tags=["Totp"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpSetupResponse",
                    {
                        "secret": serializers.CharField(),
                        "qr_code": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpSetupResponse",
                        value={"secret": "secret", "qr_code": "qr_code"},
                    )
                ],
            )
        },
    ),
    activate=extend_schema(
        tags=["Totp"],
        request=OpenApiRequest(
            request=inline_serializer(
                "TotpActivateRequest",
                {
                    "code": serializers.CharField(min_length=6, max_length=6),
                },
            ),
            examples=[
                OpenApiExample(
                    "TotpActivateRequest",
                    value={"code": "123456"},
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpActivateResponse",
                    {
                        "status": serializers.BooleanField(),
                        "recovery_codes": serializers.ListField(
                            child=serializers.CharField()
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpActivateResponse",
                        value={
                            "status": True,
                            "recovery_codes": ["123456", "654321"],
                        },
                    )
                ],
            )
        },
    ),
    verify=extend_schema(
        tags=["Totp"],
        request=OpenApiRequest(
            request=inline_serializer(
                "TotpVerifyRequest",
                {
                    "code": serializers.CharField(min_length=6, max_length=6),
                },
            ),
            examples=[
                OpenApiExample(
                    "TotpVerifyRequest",
                    value={"code": "123456"},
                )
            ],
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpVerifyResponse",
                    {
                        "access": serializers.CharField(),
                        "refresh": serializers.CharField(),
                        "user": inline_serializer(
                            "UserDataResponse",
                            {
                                "id": serializers.UUIDField(),
                                "email": serializers.EmailField(),
                                "username": serializers.CharField(),
                                "role": serializers.ChoiceField(
                                    choices=[
                                        ("customer", "Customer"),
                                        ("admin", "Admin"),
                                    ]
                                ),
                            },
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpVerifyResponse",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "user": {
                                "id": "973e1d8b-299b-4ef2-941e-82015...",
                                "email": "user@example.com",
                                "username": "example_user",
                                "role": "customer",
                            },
                        },
                    )
                ],
            )
        },
    ),
    deactivate=extend_schema(
        tags=["Totp"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpDeactivateResponse",
                    {
                        "status": serializers.BooleanField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpDeactivateResponse",
                        value={"status": True},
                    )
                ],
            )
        },
    ),
    generate_recovery_codes=extend_schema(
        tags=["Totp"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpGenerateRecoveryCodesResponse",
                    {
                        "recovery_codes": serializers.ListField(
                            child=serializers.CharField()
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpGenerateRecoveryCodesResponse",
                        value={
                            "recovery_codes": ["123456", "654321"],
                        },
                    )
                ],
            )
        },
    ),
    recovery_codes=extend_schema(
        tags=["Totp"],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    "TotpRecoveryCodesResponse",
                    {
                        "recovery_codes": serializers.ListField(
                            child=serializers.CharField()
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "TotpRecoveryCodesResponse",
                        value={
                            "recovery_codes": ["123456", "654321"],
                        },
                    )
                ],
            )
        },
    ),
    verify_recovery_code=extend_schema(
        tags=["Totp"],
        request=OpenApiRequest(
            request=inline_serializer(
                "TotpVerifyRecoveryCodeRequest",
                {
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                    "user": inline_serializer(
                        "UserResponse",
                        {
                            "id": serializers.UUIDField(),
                            "email": serializers.EmailField(),
                            "username": serializers.CharField(),
                            "role": serializers.ChoiceField(
                                choices=[
                                    ("customer", "Customer"),
                                    ("admin", "Admin"),
                                ]
                            ),
                        },
                    ),
                },
            ),
            examples=[
                OpenApiExample(
                    "TotpVerifyResponse",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": "973e1d8b-299b-4ef2-941e-82015...",
                            "email": "user@example.com",
                            "username": "example_user",
                            "role": "customer",
                        },
                    },
                )
            ],
        ),
    ),
)
