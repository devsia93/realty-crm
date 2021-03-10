from django.db import models

from realty.custom_decimal_field import CustomDecimalField
from realty.models import TypeLayout, TypeRealty, TypeMaterial
from realty.models.client import Client


class Realty(models.Model):
    class DEAL:
        """
        Тип договора
        """
        UNKNOWN = 0
        SALE = 1
        RENT = 2

        CHOICES = (
            (UNKNOWN, 'Не определено'),
            (SALE, 'Продажа'),
            (RENT, 'Аренда'),
        )

    address = models.CharField(max_length=128, verbose_name='Адрес')
    price = CustomDecimalField(verbose_name='Цена')
    owner = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE, related_name='realties',
                              verbose_name='Владелец')
    floor = models.IntegerField(blank=True, null=True, default=1, verbose_name='Этаж')
    floors = models.IntegerField(blank=True, null=True, default=1, verbose_name='Этажность')
    count_rooms = models.IntegerField(verbose_name='Кол-во комнат')
    square = models.CharField(max_length=64, blank=True, null=True, verbose_name='Площадь (общая/жилая/кухня)')
    type_layout = models.ForeignKey(TypeLayout, blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='realties', verbose_name='Тип планировки')
    type_material = models.ForeignKey(TypeMaterial, blank=True, null=True, on_delete=models.SET_NULL,
                                      related_name='realties', verbose_name='Тип материала')
    type_realty = models.ForeignKey(TypeRealty, blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='realties', verbose_name='Тип недвижимости')
    type_deal = models.IntegerField(choices=DEAL.CHOICES, default=DEAL.UNKNOWN, blank=True,
                                    verbose_name='Тип сделки')
    status = models.BooleanField(default=True, verbose_name='Активно?')
    comment = models.CharField(max_length=256, blank=True, null=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Недвижимость'
        verbose_name_plural = 'Недвижимости'

    def __str__(self):
        return self.address
