from rest_framework_jwt.views import refresh_jwt_token

from .views import Login, AuthIt
from django.urls import path

urlpatterns = [
    path('test/', Login.as_view()),
    path('authIt/', AuthIt.as_view()),
    path('refresh/', refresh_jwt_token)
]
