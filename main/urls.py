from django.urls import path
from rest_framework import routers

from main.views import PostsList, TestView

urlpatterns = [
    path('posts/', PostsList.as_view()),
    path('test/', TestView.as_view())
]

