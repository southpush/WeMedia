from django.db import models
from django.utils import timezone


class Posts(models.Model):
    content = models.TextField()
    # image_count = models.IntegerField(choices=list(range(0, 10)), default=0, null=False)
    image_path = models.TextField(null=True, blank=True, default='')
    is_delete = models.BooleanField(null=False, default=False)
    created_time = models.DateTimeField("发表时间", default=timezone.now)

    author = models.ForeignKey('user.Profile', null=False, on_delete=models.CASCADE)

