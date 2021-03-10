from django.contrib import admin

from realty.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('fio', 'phone', 'email', 'date_of_birthday', 'comment')
    search_fields = ('fio', 'phone', 'email', 'comment')
