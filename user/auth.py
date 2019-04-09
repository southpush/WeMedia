import datetime
import time

import jwt
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework.authentication import get_authorization_header
from rest_framework import authentication, serializers
from rest_framework import exceptions
from main import exceptions as custom_exception
from rest_framework_jwt.settings import api_settings
from django.core.cache import caches
from rest_framework_jwt.views import verify_jwt_token
from django.utils.translation import ugettext as _

from WeMedia import settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

user_cache1 = caches['user1']
user_cache2 = caches['user2']


def set_user_token_cache(username, token):
    user_cache1.set(username+'_token', token)
    user_cache2.set(username+'_token', token)


# 验证token
class TokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        username = request.META.get("HTTP_USERNAME", b'')
        if not username or not auth:
            raise exceptions.NotAuthenticated
        token_in_cache = user_cache1.get(username+"_token", user_cache2.get(username+"_token"))
        # 如果cache里没有这个username，就计算token里的信息
        if not token_in_cache:
            # try:
            #     payload = jwt_decode_handler(auth[1])
            #     print(payload)
            #     if username != payload["username"]:
            #         raise exceptions.AuthenticationFailed
            # except jwt.ExpiredSignature:
            #     msg = _('Signature has expired.')
            #     raise exceptions.ValidationError(msg)
            # except jwt.DecodeError:
            #     msg = _('Error decoding signature.')
            #     raise exceptions.ValidationError(msg)
            raise exceptions.AuthenticationFailed('Token is not in cache.')
        elif token_in_cache.encode('utf-8') != auth[1]:
            raise exceptions.AuthenticationFailed
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user.")
        if not user.profile.is_active:
            raise exceptions.AuthenticationFailed("Email has not been verified.", code='not_active')
        return user, auth[1]


def new_account_auth_email(user, to_email, base_uri):
    payload = {
        "username": user.username,
        "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=1000)).timestamp()),
        "orig_iat": int(time.time()),
    }
    token = jwt_encode_handler(payload)

    data = {
        'username': user.username,
        "verifyURL": "http://"+base_uri+"/api/v1.0/email-verification/?token="+token,
        "email": user.profile.email,
    }
    plaintext = get_template('email/verify.txt').render(data)
    htmltext = get_template("email/verify.html").render(data)

    subject, from_email = 'we-media verification email', settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject, plaintext, from_email, [to_email])
    msg.attach_alternative(htmltext, 'text/html')
    try:
        msg.send()
    except Exception as e:
        raise custom_exception.EmailSendFailException(detail=e.__repr__())

    return True


def verify_email(token):
    try:
        payload = jwt_decode_handler(token)
        if payload['exp'] < int(time.time()):
            raise exceptions.ValidationError("Signature has expired.")

    except Exception as e:
        msg = e.__repr__()
        raise exceptions.ValidationError(msg)
    return True


# 用于验证邮箱的serializer
class VerificationEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        payload = self._check_payload(attrs["token"])
        user = User.objects.get(username=payload['username'])
        if not user:
            raise exceptions.NotFound("No such user.")
        elif user.profile.is_active:
            raise exceptions.AuthenticationFailed('This user has been active.')
        user.profile.is_active = True
        user.profile.save()
        return {
            'user': user,
        }

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
            if payload['exp'] < int(time.time()):
                raise exceptions.ValidationError("Signature has expired.")
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

