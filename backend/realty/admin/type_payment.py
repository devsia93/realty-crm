from django.contrib import admin

from realty.models import TypePayment


@admin.register(TypePayment)
class TypePaymentAdmin(admin.ModelAdmin):
    ...
