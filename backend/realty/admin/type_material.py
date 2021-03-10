from django.contrib import admin

from realty.models import TypeMaterial


@admin.register(TypeMaterial)
class TypeMaterialAdmin(admin.ModelAdmin):
    ...
