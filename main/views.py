import os
import time

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models.query_utils import Q
from rest_framework import generics, status, exceptions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from WeMedia import settings
from main.models import Posts, Reply
from main.response import Response
from main.serializers import PostsSerializer, HeadImageSerializer, PostsListSerializer, ForwardSerializer, \
    ReplySerializer
from user.auth import TokenAuthentication, PublishPostsPermission, ForwardPermission, CommentPermission
from .tasks import add

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


# 获取一条微博的详细信息
class PostsDetail(APIView):
    pass


# 用户上传微博的api
class PostsUpload(APIView):
    authentication_classes = (TokenAuthentication,)
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


# 转发微博的API
# 应该有两个权限，一个发微博，一个转发微博
class ForwardView(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (PublishPostsPermission, ForwardPermission)
    serializer_class = ForwardSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response('ojbk', status.HTTP_200_OK)


# 用户评论微博
class ReplyView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (CommentPermission,)
    serializer_class = ReplySerializer

    @action(detail=False, methods=['post'])
    def upload_reply(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['delete'])
    def delete_reply(self, request):
        profile = request.user.profile
        try:
            reply = Reply.objects.filter(user=profile).get(pk=request.query_params.get('reply_id', 0))
        except Reply.DoesNotExist:
            raise exceptions.NotFound('无法找到指定评论')
        reply.is_delete = True
        reply.save()
        return Response('', status=status.HTTP_200_OK)


# 用户获取微博评论
class ReplyListView(generics.ListAPIView):
    serializer_class = ReplySerializer

    def get_queryset(self):
        try:
            post = Posts.objects.get(pk=self.request.query_params.get('post_id', 0))
        except Posts.DoesNotExist:
            raise exceptions.NotFound('无法找到该微博', code='no_such_posts')
        return post.replies.all().order_by('-created_time')

    # 获取某条评论下的所有回复
    @action(detail=True, methods=['get'])
    def reply_detail(self, request):
        try:
            reply = Reply.objects.get(pk=request.query_params.get('reply_id', 0))
        except Reply.DoesNotExist:
            raise exceptions.NotFound('无法找到指定评论', code='no_such_reply')
        serializer = self.get_serializer(reply.get_descendants(), many=True)
        return Response(serializer.data)


# 用户获取一条评论下的所有回复
class ReplyDetailView(generics.ListAPIView):
    serializer_class = ReplySerializer
    queryset = Reply.objects.all()

    def list(self, request, *args):
        try:
            reply = Reply.objects.get(pk=request.query_params.get('reply_id', 0))
        except Reply.DoesNotExist:
            raise exceptions.NotFound('无法找到指定评论', code='no_such_reply')
        serializer = self.get_serializer(reply.get_descendants(), many=True)
        return Response(serializer.data)


# 获取整个对话
class DialogueView(generics.ListAPIView):
    serializer_class = ReplySerializer

    def get_queryset(self):
        try:
            reply = Reply.objects.get(pk=self.request.query_params.get('reply_id', 0))
            if reply.is_root_node():
                raise exceptions.ParseError('根评论无法查找会话')
        except Reply.DoesNotExist:
            raise exceptions.NotFound('无法找到指定评论', code='no_such_reply')
        result = add.delay(2, 3)
        print(result)
        return reply.get_family().filter(Q(user=reply.user) | Q(user=reply.parent.user))


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


