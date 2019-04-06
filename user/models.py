from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enum import Enum


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
    nickname = models.CharField(max_length=20, verbose_name='微博名', unique=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=False)
    is_admin = models.BooleanField(_('admin'), default=False)
    head_img = models.ImageField(_('users/head image'), upload_to='head_img', default='default_head.png')
    gender = models.CharField(choices=gender_choices, max_length=1, default='3')
    introduction = models.CharField(max_length=140, null=True)
    registration_date = models.DateField('用户创建时间', default=timezone.now)

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


