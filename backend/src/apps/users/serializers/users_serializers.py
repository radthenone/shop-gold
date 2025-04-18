from rest_framework import serializers

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
