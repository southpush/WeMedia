from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator

from user.models import Profile


class NewAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=128, required=True)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"],
                                        password=validated_data['password'])
        profile = Profile.objects.create(email=validated_data['email'],
                                         user=user)
        return user, profile

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username',)
            ),
            UniqueTogetherValidator(
                queryset=Profile.objects.all(),
                fields=('email',)
            )
        ]


class DeleteUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)















