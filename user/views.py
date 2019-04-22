from datetime import datetime
# Create your views here.
from django.contrib.auth.models import User, Group
from django.core.cache import caches
from rest_framework import status
# from rest_framework.response import Response
from rest_framework import generics
from rest_framework import mixins
from rest_framework.decorators import authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from main.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer, RefreshJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework.authentication import get_authorization_header

from .serializers import NewAccountSerializer, DeleteUserSerializer, UserProfileForUserSerializer

from user.auth import TokenAuthentication, set_user_token_cache, new_account_auth_email, \
    VerificationEmailSerializer, PublishPostsPermission, TokenAuthenticationNotActive

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
    permission_classes = (PublishPostsPermission, )

    def get(self, request):
        return Response('hello world')


# 创建新用户
class CreateAccount(APIView):
    serializer_class = NewAccountSerializer

    def post(self, request):
        serializer = NewAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, profile = serializer.create(serializer.validated_data)
        token = new_account_auth_email(user=user, to_email=user.profile.email,
                               base_uri=request.get_host())
        return Response(data={'token': token}, status=status.HTTP_200_OK)


# 验证用户的邮箱
class EmailVerification(APIView):
    def get(self, request, *args, **kwargs):
        serializer = VerificationEmailSerializer(data=request.query_params)

        if serializer.is_valid(raise_exception=True):
            # 验证信息后授予基本权限
            user = serializer.validated_data['user']
            group = Group.objects.get(name='base_permission')
            user.groups.add(group)
            return Response('ok', status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_200_OK)


# 给用户发送验证邮箱的邮件
class EmailVerificationSend(APIView):
    authentication_classes = (TokenAuthenticationNotActive, )

    def post(self, request):
        user = request.user
        token = new_account_auth_email(user=user, to_email=user.profile.email,
                                       base_uri=request.get_host())
        return Response(data={'token': token}, status=status.HTTP_200_OK)


# 普通用户查看或修改个人信息的
class UserProfileUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = UserProfileForUserSerializer
    authentication_classes = (TokenAuthentication, )
    lookup_field = 'username'
    queryset = User.objects.all()

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj.profile


# 调试用的设置普通管理员
class SetAdmin(APIView):
    def get(self, request):
        username = request.query_params["username"]
        user = User.objects.get(username=username)
        user.profile.is_admin = True
        user.save()
        return Response('ojbk', status.HTTP_200_OK)





















