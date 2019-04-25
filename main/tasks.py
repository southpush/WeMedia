# 放应用的异步方法
from __future__ import absolute_import
from celery import shared_task


@shared_task
def add(x, y):
    return x + y

