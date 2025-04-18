from rest_framework import serializers


class TOTPStatusSerializer(serializers.Serializer):
    is_enabled = serializers.BooleanField(read_only=True)


class TOTPSetupSerializer(serializers.Serializer):
    qr_code_svg = serializers.CharField(read_only=True)

    @staticmethod
    def validate_qr_code_svg(value):
        if not value:
            raise serializers.ValidationError("QR code SVG is required.")

        if value.startswith("<svg") and value.endswith("</svg>"):
            return value


class TOTPCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    client_time = serializers.IntegerField(required=False)

    @staticmethod
    def validate_code(value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Invalid TOTP code.")
        return value


class TOTPStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    recovery_codes = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class RecoveryCodesSerializer(serializers.Serializer):
    recovery_codes = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )


class RecoveryCodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    @staticmethod
    def validate_code(value):
        if not value or len(value) < 6:
            raise serializers.ValidationError("Invalid recovery code.")
        return value
