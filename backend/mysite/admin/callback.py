from django.contrib import admin

from mysite.models import Callback


@admin.register(Callback)
class CallbackAdmin(admin.ModelAdmin):
    list_display = ('fio', 'phone', 'status')
    search_fields = ('fio', 'phone')
    list_filter = ('status',)
