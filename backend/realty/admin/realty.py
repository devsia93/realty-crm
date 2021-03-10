from django.contrib import admin

from realty.models import Realty


@admin.register(Realty)
class RealtyAdmin(admin.ModelAdmin):
    list_display = ('address',
                    'price',
                    'get_floor',
                    'count_rooms',
                    'type_layout',
                    'type_material',
                    'type_realty',
                    'type_deal',
                    'square',
                    'status',
                    'owner',
                    'get_worker_by_owner',
                    'comment')
    search_fields = ('owner__fio',
                     'owner__email',
                     'owner__phone',
                     'owner__worker__fio',
                     'address',
                     'comment')
    list_filter = ('status',)

    def get_floor(self, obj):
        return f'{obj.floor}/{obj.floors}'

    def get_worker_by_owner(self, obj):
        return obj.owner.worker

    get_floor.short_description = 'Этаж'
    get_worker_by_owner.short_description = 'Работник'
