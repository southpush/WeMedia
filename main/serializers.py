import time

from django.utils import timezone
from rest_framework import serializers, exceptions

from main.models import Posts, PostsImages


class PostsListSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Posts
        fields = ('id', 'content', "created_time_timestamp", 'author', 'images')

    def create(self, validated_data):
        pass


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

    def create(self, validated_data):
        profile = self.context['request'].user.profile
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


class HeadImageSerializer(serializers.Serializer):
    head_img = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=False)

    def validate(self, attrs):
        print(attrs)
        return attrs
