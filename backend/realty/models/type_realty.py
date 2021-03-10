from django.db import models


class TypeRealty(models.Model):
    title = models.CharField(max_length=32, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип недвижимости'
        verbose_name_plural = 'Типы недвижимости'

    def __str__(self):
        return self.title
