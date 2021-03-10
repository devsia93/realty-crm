from django.contrib import admin

from realty.models import TypeRealty


@admin.register(TypeRealty)
class TypeRealtyAdmin(admin.ModelAdmin):
    ...
