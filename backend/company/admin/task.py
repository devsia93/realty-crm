from django.contrib import admin

from company.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('text', 'worker', 'deal', 'priority', 'status', 'date_start', 'date_end')
    list_filter = ('status', 'priority')
    search_fields = ('text', 'worker__fio')
