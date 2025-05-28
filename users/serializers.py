import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import User


class CustomRoleField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(choices=User.ROLE_CHOICES, **kwargs)
        self.valid_keys = {choice[0] for choice in User.ROLE_CHOICES}

    def to_internal_value(self, data):
        if data not in self.valid_keys:
            raise serializers.ValidationError("Role must be one of: 'admin' or 'agent'.")
        return super().to_internal_value(data)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    role = CustomRoleField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username','password', 'role']
        read_only_fields = ['id']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        rules = [
            (r'[A-Z]', "at least one uppercase letter"),
            (r'[a-z]', "at least one lowercase letter"),
            (r'[0-9]', "at least one digit"),
            (r'[!@#$%^&*(),.?\":{}|<>]', "at least one special character"),
        ]

        failed_rules = [msg for regex, msg in rules if not re.search(regex, value)]
        if failed_rules:
            raise serializers.ValidationError([f"Password must contain {msg}." for msg in failed_rules])

        return value

    def _set_user_password(self, user, password):
        user.set_password(password)
        user.save()
        return user

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        return self._set_user_password(user, password)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            self._set_user_password(instance, password)
        else:
            instance.save()
        return instance