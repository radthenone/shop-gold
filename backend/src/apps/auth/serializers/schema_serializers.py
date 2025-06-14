from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


@extend_schema_serializer(component_name="UserDataResponse")
class UserDataResponseSerializer(serializers.Serializer):
    """
    Serializer for user data response.
    """

    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.ChoiceField(
        choices=[("customer", "Customer"), ("admin", "Admin")]
    )
