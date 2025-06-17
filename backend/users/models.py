from django.contrib.auth.models import AbstractUser
from django.db import models


class ProjectUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Почта')
    avatar = models.ImageField(
        upload_to='users/',
        verbose_name='Аватар',
        null=True,
        blank=True,
        default=''
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
