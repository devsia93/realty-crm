from django.contrib import admin

from company.models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birthday', 'sex')
    list_filter = ('sex',)
    search_fields = ('name',)
    ordering = ('-date_of_birthday',)
