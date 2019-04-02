from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.utils.translation import gettext_lazy as _
import time
from django.utils import timezone


class User(AbstractUser):
    pass


