from django.urls import path
from rest_framework import routers

from main.views import PostsList, TestView, PostsUpload, ForwardView, ReplyView, \
    ReplyListView, ReplyDetailView, DialogueView

urlpatterns = [
    path('', PostsList.as_view()),
    path('upload/', PostsUpload.as_view()),
    path('forward/', ForwardView.as_view()),
    path('reply/', ReplyView.as_view({'post': 'upload_reply', 'delete': 'delete_reply'})),
    path('reply/list/', ReplyListView.as_view()),
    path('reply/detail/', ReplyDetailView.as_view()),
    path('reply/dialogue/', DialogueView.as_view())

]
