from datetime import timedelta

from allauth.account.models import EmailConfirmation
from allauth.socialaccount.models import EmailAddress
from allauth.utils import get_username_max_length
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Profile, User
from apps.users.tasks import check_email_confirmation
from core.adapters import get_adapter


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
            "password1": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def profile_save(self, user):
        profile = Profile.objects.create(user=user)
        profile.first_name = self.validated_data.get("first_name", "")
        profile.last_name = self.validated_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "phone"])

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

        check_email_confirmation.apply_async(
            args=[email_address.id], expires=timezone.now() + timedelta(minutes=15)
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    key = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email_confirmation = None

    def validate_key(self, key):
        try:
            self.email_confirmation = EmailConfirmation.objects.get(key=key)
        except EmailConfirmation.DoesNotExist as error:
            raise serializers.ValidationError("Invalid key") from error
        return key

    def save(self, request):
        try:
            self.email_confirmation.confirm(request)
            user = self.email_confirmation.email_address.user
            user.is_active = True
            user.save(update_fields=["is_active"])
            return user
        except Exception as error:
            raise serializers.ValidationError(
                f"Error confirming email: {error!s}"
            ) from error


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
        adapter = get_adapter()
        try:
            confirmation = EmailConfirmation.objects.get(email_address=email_address)
            update_fields = ["sent", "key"]
        except EmailConfirmation.DoesNotExist:
            confirmation = EmailConfirmation.create(email_address)
            update_fields = None

        confirmation.sent = timezone.now()
        confirmation.key = adapter.generate_emailconfirmation_key(email_address.email)
        confirmation.save(update_fields=update_fields)

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
        check_email_confirmation.apply_async(
            args=[email_address.id], expires=timezone.now() + timedelta(minutes=15)
        )

        return email_address.user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


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

    def to_representation(self, instance):
        return {
            "access": instance["access"],
            "refresh": instance["refresh"],
        }
