from datetime import datetime
# Create your views here.
from django.contrib.auth.models import User
from django.core.cache import caches
from rest_framework import status
# from rest_framework.response import Response
from main.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer, RefreshJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework.authentication import get_authorization_header

from .serializers import NewAccountSerializer, DeleteUserSerializer

from user.auth import TokenAuthentication, set_user_token_cache, new_account_auth_email, \
    VerificationEmailSerializer

user_cache1 = caches['user1']
user_cache2 = caches['user2']

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


# 登陆获取token
class Login(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            print(response_data)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 将token放入缓存
            set_user_token_cache(user.username, token)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        serializer = DeleteUserSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            user.delete()
            return Response('ok')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 刷新token
class RefreshToken(JSONWebTokenAPIView):
    serializer_class = RefreshJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        token = get_authorization_header(request).split()[1].decode('utf-8')

        serializer = self.get_serializer(data={"token": token})

        if serializer.is_valid(raise_exception=True):
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
            # cache中加入token
            set_user_token_cache(user.username, token)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthIt(APIView):
    authentication_classes = (TokenAuthentication, )

    def get(self, request):
        print(request.user)
        return Response('hello world')


# 创建新用户
class CreateAccount(APIView):
    serializer_class = NewAccountSerializer

    def post(self, request):
        serializer = NewAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, profile = serializer.create(serializer.validated_data)
        new_account_auth_email(user=user, to_email=user.profile.email,
                               base_uri=request.get_host())
        return Response(status=status.HTTP_200_OK)


# 验证用户的邮箱
class EmailVerification(JSONWebTokenAPIView):
    serializer_class = VerificationEmailSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)

        if serializer.is_valid(raise_exception=True):
            return Response('ok', status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


























