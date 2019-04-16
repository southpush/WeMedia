from rest_framework import serializers

from main.models import Posts


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Posts
        fields = ('content', 'image_path', 'is_delete', "created_time", 'author')

    def create(self, validated_data):
        pass

