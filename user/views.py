from datetime import datetime

import jwt
from django.contrib.auth.models import User
# Create your views here.
from django.core.cache import caches
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework import exceptions
from django.utils.translation import ugettext as _
from rest_framework_jwt.views import refresh_jwt_token


jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
user_cache = caches['user']


class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        username = request.META.get("HTTP_USERNAME", b'')
        if not username or not auth:
            raise exceptions.NotAuthenticated
        token_in_cache = user_cache.get(username+"_token")
        # 如果cache里没有这个username，就计算token里的信息
        if not token_in_cache:
            try:
                payload = jwt_decode_handler(auth[1])
                print(payload)
                if username != payload["username"]:
                    raise exceptions.AuthenticationFailed
            except jwt.ExpiredSignature:
                msg = _('Signature has expired.')
                raise exceptions.ValidationError(msg)
            except jwt.DecodeError:
                msg = _('Error decoding signature.')
                raise exceptions.ValidationError(msg)
        elif token_in_cache.encode('utf-8') != auth[1]:
            raise exceptions.AuthenticationFailed
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user.")
        return user, auth[1]


class Login(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 将token放入缓存
            user_cache.set(user.username + '_token', token)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthIt(APIView):
    authentication_classes = (TokenAuthentication, )

    def get(self, request, *args, **kwargs):
        return Response('hello world')
