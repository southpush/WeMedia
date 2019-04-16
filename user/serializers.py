from django.db.utils import IntegrityError
from rest_framework import serializers, exceptions
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator

from user.models import Profile


class NewAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=128, required=True)

    def create(self, validated_data):
        try:
            user = User.objects.create(username=validated_data["username"])
            user.set_password(validated_data['password'])
            user.save()
        except Exception as e:
            raise exceptions.NotAcceptable(e.__repr__(), code="fail_to_create_user")
        try:
            profile = Profile.objects.create(email=validated_data['email'],
                                            user=user)
        except Exception as e:
            user.delete()
            raise exceptions.NotAcceptable(e.__repr__(), code="fail_to_create_user")
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


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )
        read_only_fields = ('username', )


class UserProfileForUserSerializer(serializers.ModelSerializer):

    user = UsernameSerializer()

    class Meta:
        model = Profile
        fields = ('nickname', 'user', "is_active", 'head_img', 'gender', 'introduction',
                  'registration_date', 'email')
        read_only_fields = ('user', 'is_active', "registration_data")













