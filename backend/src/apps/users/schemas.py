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
                    "first_name": serializers.CharField(required=False),
                    "last_name": serializers.CharField(required=False),
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
                    )
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
)
