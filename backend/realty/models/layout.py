from django.db import models


class Layout(models.Model):
    title = models.CharField(max_length=32, verbose_name='Название')

    class Meta:
        verbose_name = 'Планировка'
        verbose_name_plural = 'Планировки'
