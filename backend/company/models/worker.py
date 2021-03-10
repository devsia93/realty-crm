from django.contrib.auth.models import AbstractUser
from django.db import models


class Worker(AbstractUser):
    username = models.CharField(max_length=16, unique=True, verbose_name='Псевдоним')
    password = models.CharField(max_length=255, verbose_name='Пароль')
    email = models.EmailField(blank=True, verbose_name='Адрес эл.почты')
    last_name = models.CharField(max_length=32, verbose_name='Фамилия')
    first_name = models.CharField(max_length=32, default='admin', verbose_name='Имя')
    middle_name = models.CharField(max_length=32, blank=True, verbose_name='Отчество')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Телефон')
    date_of_birthday = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'
