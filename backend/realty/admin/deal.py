from django.contrib import admin

from realty.models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('main_worker',
                    'sub_worker',
                    'realty',
                    'client',
                    'amount',
                    'amount_commission',
                    'type_payment',
                    'date_of_deal',
                    'agreement')
    search_fields = ('main_worker__fio',
                     'sub_worker__fio',
                     'client__fio',
                     'main_worker__email',
                     'sub_worker__email',
                     'client__email',
                     'main_worker__phone',
                     'sub_worker__phone',
                     'client__phone')
    list_filter = ('type_payment',)
