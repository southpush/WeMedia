from .views import Login, AuthIt, RefreshToken, CreateAccount, EmailVerification
from django.urls import path

urlpatterns = [
    path('login/', Login.as_view()),
    path('authIt/', AuthIt.as_view()),
    path('refresh-token/', RefreshToken.as_view()),
    path('signup/', CreateAccount.as_view()),
    path('email-verification/', EmailVerification.as_view())
]
