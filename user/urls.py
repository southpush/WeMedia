from .views import Login, AuthIt
from django.urls import path

urlpatterns = [
    path('test/', Login.as_view()),
    path('authIt/', AuthIt.as_view())
]
