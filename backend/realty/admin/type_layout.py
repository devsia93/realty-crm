from django.contrib import admin

from realty.models import TypeLayout


@admin.register(TypeLayout)
class TypeLayoutAdmin(admin.ModelAdmin):
    ...
