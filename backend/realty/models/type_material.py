from django.db import models


class TypeMaterial(models.Model):
    title = models.CharField(max_length=32, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип материала'
        verbose_name_plural = 'Типы материалов'

    def __str__(self):
        return self.title
