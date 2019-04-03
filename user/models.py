from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    # 一对一外键，设置删除级联
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, verbose_name='微博名', unique=True)

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)


