from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_MAX_LENGTH, FIRST_LAST_NAME_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_LAST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=FIRST_LAST_NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription',
            ),
        ]
