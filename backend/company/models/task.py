from django.db import models

from company.models import Worker


class Task(models.Model):
    class PRIORITY:
        LOW = 0
        MIDDLE = 1
        HIGH = 2

        CHOICES = (
            (LOW, 'Низкий'),
            (MIDDLE, 'Средний'),
            (HIGH, 'Высокий'),
        )

    text = models.CharField(max_length=256, verbose_name='Текст')
    date_start = models.DateField(verbose_name='Дата начала')
    date_end = models.DateField(verbose_name='Дата окончания')
    priority = models.IntegerField(choices=PRIORITY.CHOICES, default=PRIORITY.MIDDLE, verbose_name='Приоритет')
    worker = models.ForeignKey(Worker, blank=True, null=True, on_delete=models.CASCADE, related_name='tasks',
                               verbose_name='Сотрудник')
    deal = models.ForeignKey('realty.Deal', blank=True, null=True, on_delete=models.SET_NULL, related_name='tasks',
                             verbose_name='Сделка')
    status = models.BooleanField(default=False, verbose_name='Статус')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f'Задача #{self.id}'
