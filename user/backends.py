from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):

    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        if email is None:
            if username is None:
                return None
            else:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist as e:
                    print(e)
                    return None
        else:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist as e:
                print(e)
                return None

        if user.check_password(password):
            return user
