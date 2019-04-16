from .views import Login, AuthIt, RefreshToken, CreateAccount, \
    EmailVerification, UserProfileUpdate, SetAdmin, EmailVerificationSend
from django.urls import path

urlpatterns = [
    path('login/', Login.as_view()),
    path('authIt/', AuthIt.as_view()),
    path('refresh-token/', RefreshToken.as_view()),
    path('signup/', CreateAccount.as_view()),
    path('email-verification/', EmailVerification.as_view()),
    path('send-verification-email/', EmailVerificationSend.as_view()),
    path('user-info/<str:username>/', UserProfileUpdate.as_view()),
    path('setAdmin/', SetAdmin.as_view()),

]
