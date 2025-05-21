from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    social_links = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'role_display',
            'first_name',
            'last_name',
            'bio',
            'profile_picture',
            'profile_picture_url',
            'date_of_birth',
            'age',
            'phone_number',
            'website',
            'twitter_handle',
            'linkedin_profile',
            'social_links',
            'created_at',
            'updated_at',
            'is_student',
            'is_instructor',
            'is_admin'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'profile_picture': {'write_only': True},
            'date_of_birth': {'write_only': True}
        }
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'is_student', 'is_instructor', 'is_admin'
        ]

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None

    def get_social_links(self, obj):
        return {
            'twitter': f"https://twitter.com/{obj.twitter_handle}" if obj.twitter_handle else None,
            'linkedin': obj.linkedin_profile,
            'website': obj.website
        }

    def get_age(self, obj):
        from datetime import date
        if obj.date_of_birth:
            today = date.today()
            return today.year - obj.date_of_birth.year - (
                (today.month, today.day) <
                (obj.date_of_birth.month, obj.date_of_birth.day)
            )
        return None

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class UserCreateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['password']
        extra_kwargs = {
            **UserSerializer.Meta.extra_kwargs,
            'password': {'write_only': True, 'required': True}
        }

class PublicUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            'id',
            'username',
            'role_display',
            'bio',
            'profile_picture_url',
            'social_links',
            'created_at'
        ]


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        write_only=True
    )

    def validate_new_password(self, value):
        return value