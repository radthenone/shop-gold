from allauth.account.adapter import get_adapter
from allauth.account.models import EmailConfirmation
from allauth.account.utils import setup_user_email
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import EmailAddress
from allauth.utils import get_username_max_length
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DefaultRegisterSerializer,
)
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.adapters import AccountAdapter
from apps.users.models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.CharField(source="get_avatar_url", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "avatar_url",
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "profile",
            "full_name",
            "role",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "date_joined",
            "role",
        )


class RegisterSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaned_data = None

    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=5,
        required=True,
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    rewrite_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)

    @staticmethod
    def validate_username(username):
        username = get_adapter().clean_username(username)
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists.")
        return username

    @staticmethod
    def validate_email(email):
        email = get_adapter().clean_email(email)
        if EmailAddress.objects.filter(email=email, verified=True).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    @staticmethod
    def validate_password(password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data["password"] != data["rewrite_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def profile_save(self, user):
        profile = Profile.objects.create(user=user)
        profile.first_name = self.validated_data.get("first_name", "")
        profile.last_name = self.validated_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name"])

    @staticmethod
    def email_address_save(user: "User"):
        email_address = EmailAddress.objects.create(
            user=user,
            email=user.email,
            primary=True,
            verified=False,
        )
        return email_address

    @staticmethod
    def email_confirmation_save(email_address: "EmailAddress"):
        confirmation = EmailConfirmation.create(email_address)
        confirmation.sent = timezone.now()
        confirmation.save()
        return confirmation

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self)

        self.profile_save(user)
        email_address = self.email_address_save(user)
        confirmation = self.email_confirmation_save(email_address)
        adapter.send_confirmation_mail(
            request,
            confirmation,
            signup=True,
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    @staticmethod
    def validate_code(code):
        try:
            EmailConfirmation.objects.get(key=code)
        except EmailConfirmation.DoesNotExist as error:
            raise serializers.ValidationError("Invalid code") from error
        return code

    def save(self, request):
        code = self.validated_data["code"]
        email_confirmation = EmailConfirmation.objects.get(key=code)
        email_confirmation.confirm(request)
        return email_confirmation.email_address.user


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        try:
            self.email_address_get(email, verified=False)
        except EmailAddress.DoesNotExist as error:
            raise serializers.ValidationError(
                "Email address is already verified or does not exist."
            ) from error
        return email

    @staticmethod
    def email_address_get(email: str, verified: bool = False) -> "EmailAddress":
        email_address = EmailAddress.objects.get(
            email=email,
            verified=verified,
        )
        return email_address

    @staticmethod
    def email_confirmation_update(email_address: "EmailAddress") -> "EmailConfirmation":
        confirmation = EmailConfirmation.objects.get(email_address=email_address)
        confirmation.sent = timezone.now()
        adapter = get_adapter()
        confirmation.key = adapter.generate_emailconfirmation_key(email_address.email)
        confirmation.save(update_fields=["sent", "key"])
        return confirmation

    def save(self, request):
        email = self.validated_data["email"]
        email_address = self.email_address_get(email, verified=False)
        adapter = get_adapter()
        confirmation = self.email_confirmation_update(email_address)
        adapter.send_confirmation_mail(
            request,
            confirmation,
            signup=False,
        )
        return email_address.user


class LoginSerializer(DefaultLoginSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            msg = "Unable to log in with provided credentials."
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = "User account is disabled."
            raise serializers.ValidationError(msg)

        refresh = RefreshToken.for_user(user)

        attrs["user"] = user
        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)

        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh"])
        except TokenError as error:
            raise serializers.ValidationError("Invalid refresh token") from error

        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)

        return attrs
