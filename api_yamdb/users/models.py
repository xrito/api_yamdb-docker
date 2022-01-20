from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER_ROLES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Administrator')
    ]
    role = models.CharField(
        choices=USER_ROLES,
        default=USER,
        blank=False,
        max_length=16
    )
    auth_code = models.CharField(
        blank=True,
        max_length=5
    )
    bio = models.CharField(
        blank=True,
        max_length=10000
    )
