import os
import time

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import generics, status, exceptions
from rest_framework.views import APIView

from WeMedia import settings
from main.models import Posts
from main.response import Response
from main.serializers import PostsSerializer, HeadImageSerializer, PostsListSerializer
from user.auth import TokenAuthentication, PublishPostsPermission


# 获取用户微博列表的api（不用登陆即可访问）
class PostsList(generics.ListAPIView):
    serializer_class = PostsListSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username', '')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.NotFound('no such user', code="no_such_user")
        return Posts.objects.filter(author=user.profile, is_delete=False).order_by('-created_time')


# 用户上传微博的api
class PostsUpload(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (PublishPostsPermission, )
    serializer_class = PostsListSerializer

    def post(self, request):
        serializer = PostsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(serializer.data)

    def delete(self, request):
        try:
            id = request.query_params.get('post_id', 0)
            post = request.user.profile.posts.get(id=id, is_delete=False)
        except Posts.DoesNotExist:
            raise exceptions.NotFound("no such post")
        post.is_delete = True
        post.save()
        return Response()


class TestView(APIView):
    serializer_class = HeadImageSerializer

    def post(self, request):
        serializer = HeadImageSerializer(data=request.FILES)
        if serializer.is_valid(raise_exception=True):
            # print(serializer.validated_data["head_img"])
            pass
        # print(over_write_head_image('', request.FILES.get('pic1')))
        return Response('ooook', status=status.HTTP_200_OK)


def over_write_head_image(original_path, img):
    if not original_path == "/media/head_img/default_head.png":
        if os.path.exists(original_path):
            os.remove(os.path.join(settings.BASE_DIR, original_path))

    suffix = img.name.split('.')[-1]
    path = default_storage.save(
        'head_img/'+str(int(time.time()))+"."+suffix, ContentFile(img.read()))
    return path


