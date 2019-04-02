# from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.validators import UnicodeUsernameValidator
# from django.db import models
#
#
# class OrdinaryUser(AbstractBaseUser):
#     username_validator = UnicodeUsernameValidator()
#
#     username = models.CharField(
#         _('username'),
#         max_length=20,
#         unique=True,
#         validators=[username_validator],
#         error_messages={
#             'unique': _("A user with that username already exists."),
#         },
#     )
#
