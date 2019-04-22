from django.db import models
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Posts(models.Model):
    content = models.CharField(max_length=200)
    is_delete = models.BooleanField(null=False, default=False)
    created_time = models.DateTimeField("发表时间", default=timezone.now)

    author = models.ForeignKey('user.Profile', null=False, related_name='posts', on_delete=models.CASCADE)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True)

    # 是否转发的微博
    is_forward = models.BooleanField(default=False)

    @property
    def created_time_timestamp(self):
        return self.created_time.timestamp()


# 保存微博图片的表
class PostsImages(models.Model):
    post = models.ForeignKey('main.Posts', null=False, related_name='images', on_delete=models.CASCADE)
    profile = models.ForeignKey('user.Profile', null=False, related_name='images', on_delete=models.CASCADE)

    image = models.ImageField('posts/image', upload_to='posts', default=None, null=True, blank=True)

    def __str__(self):
        return self.image.url


# 微博评论的表
# class Comment(models.Model):
#     post = models.ForeignKey('main.Posts', null=False, related_name='comments', on_delete=models.CASCADE)
#     user = models.ForeignKey('user.Profile', null=False, related_name='comments', on_delete=models.CASCADE)
#
#     content = models.CharField(null=False, max_length=150)
#     created_time = models.DateTimeField(default=timezone.now)


# 回复表
# class Reply(models.Model):
#     comment = models.ForeignKey('main.Comment', null=False, related_name='replies', on_delete=models.CASCADE)
#     user = models.ForeignKey('user.Profile', null=False, related_name='reply', on_delete=models.CASCADE)
#     parent = models.ForeignKey('self', null=True, blank=True, default=None,
#     on_delete=models.SET('self.parent.parent'))
#     content = models.CharField(max_length=150, null=False)
#     created_time = models.DateTimeField(default=timezone.now)


# 转发表
# class Forward(models.Model):
#     posts = models.OneToOneField('main.Posts', null=False, related_name='forwards_message', on_delete=models.CASCADE)
#     # 转发别人转发的微博
#     from_posts = models.ForeignKey('main.Posts', null=True, related_name='forwards_l2', on_delete=models.CASCADE,
#                                    default=None, blank=True)
#
#     # 最开始转发的那条微博
#     origin_posts = models.ForeignKey('main.Posts', null=False, related_name='forwards_l1', on_delete=models.CASCADE)


# 测试mptt
class Genre(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

