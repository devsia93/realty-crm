from django.db import models


class Callback(models.Model):
    class STATUS:
        NO_ACTIVE = 0
        ACTIVE = 1

        CHOICES = (
            (NO_ACTIVE, 'Неактивен'),
            (ACTIVE, 'Активен'),
        )

    fio = models.CharField(max_length=128, verbose_name='ФИО')
    phone = models.CharField(max_length=32, verbose_name='Телефон')
    status = models.IntegerField(default=STATUS.ACTIVE, choices=STATUS.CHOICES, blank=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'

    def __str__(self):
        return self.fio
