import time

from django.utils import timezone
from rest_framework import serializers, exceptions

from main.models import Posts, PostsImages, Reply


class PostsListSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Posts
        fields = ('id', 'content', "created_time_timestamp", 'author', 'images', 'reply_count', 'forward_count',
                  'like_count')


# 用于用户发表微博的序列化器
class PostsSerializer(serializers.Serializer):
    pic1 = serializers.ImageField(max_length=None, use_url=False, required=False)
    pic2 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic3 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic4 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic5 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic6 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic7 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic8 = serializers.ImageField(max_length=None, required=False, use_url=False)
    pic9 = serializers.ImageField(max_length=None, required=False, use_url=False)

    content = serializers.CharField(max_length=200, min_length=1)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        profile = validated_data['user'].profile
        post = Posts.objects.create(content=validated_data['content'], author=profile)
        try:
            for num in range(1, 10):
                pic = validated_data.get('pic'+str(num), '')
                if pic:
                    pic.name = str(int(timezone.now().timestamp())) + '.' + pic.name.split('.')[-1]
                    PostsImages.objects.create(image=pic, post=post, profile=profile)
        except Exception as e:
            post.delete()
            raise exceptions.ParseError(e.__repr__())
        return post


# 用于用户转发微博的序列化器
class ForwardSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=150)
    parent_id = serializers.IntegerField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # 验证数据，主要是验证有没有该parent
    def validate(self, attrs):
        parent_id = attrs['parent_id']
        try:
            parent = Posts.objects.get(id=parent_id)
        except Posts.DoesNotExist:
            raise exceptions.NotFound('转发的微博不存在', code='no_such_posts')
        if parent.is_delete:
            raise exceptions.NotFound("该转发的微博已被删除", code='has_been_deleted')
        self.parent = parent
        return attrs

    def create(self, validated_data):
        profile = validated_data['user'].profile
        try:
            post = Posts.objects.create(content=validated_data['content'], parent=self.parent,
                                        author=profile)
        except Exception as e:
            raise exceptions.ParseError(e.__repr__())
        return post


# 发表微博评论的序列化器
class ReplySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def create(self, validated_data):
        try:
            reply = Reply.objects.create(content=validated_data['content'], user=validated_data['user'].profile,
                                         parent=validated_data.get('parent', None), posts=validated_data['posts'])
        except Exception as e:
            raise exceptions.ParseError(e.__repr__())
        return reply

    class Meta:
        model = Reply
        fields = ('id', 'content', 'created_time_timestamp', 'user', 'parent', 'posts', 'son_reply_count',
                  'from_user_head', 'from_user_nickname', 'to_user_nickname')
        read_only_fields = ('created_time', )
































class HeadImageSerializer(serializers.Serializer):
    head_img = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False)

    def validate(self, attrs):
        print(attrs)
        return attrs
