from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Posts(MPTTModel):
    content = models.CharField(verbose_name='微博正文', max_length=200)
    is_delete = models.BooleanField(verbose_name='是否删除', null=False, default=False)
    created_time = models.DateTimeField(verbose_name="发表时间", default=timezone.now)

    author = models.ForeignKey('user.Profile', verbose_name='创建用户', null=False, related_name='posts', on_delete=models.CASCADE)

    parent = TreeForeignKey('self', verbose_name='源微博', on_delete=models.CASCADE, default=None, null=True, blank=True)

    # 获取创建时间的时间戳
    @property
    def created_time_timestamp(self):
        return self.created_time.timestamp()

    # 获取转发数
    @property
    def forward_count(self):
        return self.get_descendant_count()

    @property
    def like_count(self):
        return self.like.all().__len__()

    @property
    def reply_count(self):
        return self.replies.all().__len__()

    class MPTTMeta:
        order_insertion_by = ['-created_time']


# 保存微博图片的表
class PostsImages(models.Model):
    post = models.ForeignKey('main.Posts', null=False, related_name='images', on_delete=models.CASCADE)
    profile = models.ForeignKey('user.Profile', null=False, related_name='images', on_delete=models.CASCADE)

    image = models.ImageField('posts/image', upload_to='posts', default=None, null=True, blank=True)

    def __str__(self):
        return self.image.url


# 微博评论表，用mptt
class Reply(MPTTModel):
    user = models.ForeignKey('user.Profile', null=False, related_name='replies', on_delete=models.CASCADE)
    content = models.CharField(null=False, max_length=150)
    created_time = models.DateTimeField(default=timezone.now)
    is_delete = models.BooleanField(null=False, default=False)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='replies', default=None, null=True,
                            blank=True)
    posts = models.ForeignKey('main.Posts', on_delete=models.CASCADE, related_name='replies', default=None,
                              null=True, blank=True)

    @property
    def from_user_head(self):
        return self.user.head_img.url

    @property
    def from_user_nickname(self):
        return self.user.nickname

    @property
    def to_user_nickname(self):
        if self.parent:
            return self.parent.user.nickname
        else:
            return None

    @property
    def created_time_timestamp(self):
        return self.created_time.timestamp()

    class MPTTMeta:
        order_insertion_by = ['-created_time']

    @property
    def son_reply_count(self):
        return self.get_descendant_count() if self.is_root_node() else None


# 保存点赞的表
class Like(models.Model):
    user = models.ForeignKey('user.Profile', null=False, related_name='send_like', on_delete=models.CASCADE)
    receive_user = models.ForeignKey('user.Profile', null=False, related_name='receive_like', on_delete=models.CASCADE)
    posts = models.ForeignKey('main.Posts', null=False, related_name='like', on_delete=models.CASCADE)


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
# class Genre(MPTTModel):
#     name = models.CharField(max_length=50, unique=True)
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
#
#     class MPTTMeta:
#         order_insertion_by = ['name']

