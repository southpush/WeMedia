import time
from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enum import Enum
from django.utils.crypto import get_random_string


class PermissionChoice(Enum):
    ORDINARY = 'lever0'


gender_choices = (
    ('1', "male"),
    ('2', "female"),
    ('3', "others"),
)


class Profile(models.Model):
    # 一对一外键，设置删除级联
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nickname = models.CharField(max_length=20, verbose_name='微博名',
                                unique=True, default="用户"+get_random_string(length=14))
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=False)
    is_admin = models.BooleanField(_('admin'), default=False)
    head_img = models.ImageField(_('users/head image'), upload_to='head_img', default='default_head.png')
    gender = models.CharField(choices=gender_choices, max_length=1, default='3')
    introduction = models.CharField(max_length=140, null=True, blank=True)
    registration_date = models.DateField('用户创建时间', default=timezone.now)

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)

    class Meta:
        permissions = (
            # 普通用户的权限
            ('publish_posts', "可以发微博"),
            ('comment', "可以评论微博"),
            ('forward', "可以转发微博"),
            ('like', "可以点在微博"),
            ('change_info', "可以更改个人信息"),
            # 管理员用户的权限
            ('delete_posts', "可以删除某一条微博"),
            ('publish_tips', "可以针对某一条微博发出公告"),
            ("ban_user", "可以禁言用户"),
        )


class BannedRecode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_permission = models.ForeignKey(Permission, on_delete=models.PROTECT, default=None,
                                          null=True, blank=True)
    exp_time = models.DateTimeField(auto_now_add=True, auto_now=False)


