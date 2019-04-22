from django.urls import path
from rest_framework import routers

from main.views import PostsList, TestView, PostsUpload

urlpatterns = [
    path('posts/', PostsList.as_view()),
    path('test/', TestView.as_view()),
    path('posts/upload/', PostsUpload.as_view())
]

