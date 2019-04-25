from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from celery import Celery, platforms

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WeMedia.settings')

app = Celery('WeMedia', broker='redis://127.0.0.1:6379/2')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# 允许root 用户运行celery
platforms.C_FORCE_ROOT = True

# 每个worker执行任务数量
CELERYD_MAX_TASKS_PER_CHILD = 500

# 让celery支持定时任务
app.conf.update(
    CELERYBEAT_SCHEDULE={
        # 'sum-task': {
        #     'task': 'deploy.tasks.add',
        #     'schedule':  timedelta(seconds=20),
        #     'args': (5, 6)
        # },
        # 'send-report': {
        #     'task': 'deploy.tasks.report',
        #     'schedule': crontab(hour=4, minute=30, day_of_week=1),
        # }
    }
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))