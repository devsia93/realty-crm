from django.db import models


class TypePayment(models.Model):
    title = models.CharField(max_length=16, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип оплаты'
        verbose_name_plural = 'Типы оплаты'

    def __str__(self):
        return self.title
