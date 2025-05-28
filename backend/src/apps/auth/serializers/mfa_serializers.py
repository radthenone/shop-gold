from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class TOTPCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    @staticmethod
    def validate_code(value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError(_("Invalid TOTP code."))
        return value


class RecoveryCodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    @staticmethod
    def validate_code(value):
        if not value or len(value) < 6:
            raise serializers.ValidationError(_("Invalid recovery code."))
        return value
