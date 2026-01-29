from django.contrib.auth.password_validation import validate_password

from accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=9,
        max_length=20,
        write_only=True,
        error_messages={
            "blank": "Password field may not be blank.",
            "max_length": "Ensure password field has no more than {max_length} characters.",
            "min_length": "Ensure password field has at least {min_length} characters.",
        },
    )
    smartsheet_token = serializers.CharField(max_length=512, write_only=True)

    def validate(self, attrs):
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=validated_data["password"],
        )
        user.smartsheet_token = validated_data.get("smartsheet_token", "")
        user.save()
        return user

    class Meta:
        model = User
        fields = ("id", "name", "password", "email", "smartsheet_token")


class UserProfileSerializer(serializers.ModelSerializer):
    has_smartsheet_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "name", "has_smartsheet_token")
        read_only_fields = ("email", "has_smartsheet_token")

    def get_has_smartsheet_token(self, obj):
        return bool(obj.smartsheet_token)
