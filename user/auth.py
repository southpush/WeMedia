from django.contrib.auth.models import User
from rest_framework.authentication import get_authorization_header
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
from django.core.cache import caches

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

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
        return user, auth[1]