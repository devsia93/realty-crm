from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from company.models import Worker, Child, Task
from realty.models import Client, Deal


class DealInline(admin.TabularInline):
    model = Deal
    fk_name = 'main_worker'
    fields = ('realty', 'sub_worker', 'client', 'amount', 'amount_commission', 'type_payment', 'date_of_deal', 'agreement')
    extra = 0

    def get_queryset(self, request):
        path = request.path
        current_worker_id = ''
        for i in range(len(path)):
            if path[i].isnumeric():
                current_worker_id += path[i]
                if not path[i+1].isnumeric():
                    break
        if current_worker_id:
            return Deal.objects.filter(Q(main_worker=int(current_worker_id)) | Q(sub_worker=int(current_worker_id)))
        else:
            return super().get_queryset(request)


class TaskInline(admin.TabularInline):
    model = Task
    fields = ('text', 'worker', 'priority', 'status', 'date_start', 'date_end',)
    extra = 0


class ChildInline(admin.TabularInline):
    model = Child
    fields = ('name', 'date_of_birthday', 'sex')
    extra = 0


class ClientInline(admin.TabularInline):
    model = Client
    fields = ('fio', 'phone', 'email', 'date_of_birthday', 'comment')
    extra = 0


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = ('get_fio', 'phone', 'date_of_birthday')
    search_fields = ('get_fio', 'phone')
    inlines = (DealInline, ClientInline, ChildInline)
    readonly_fields = ('date_joined',)

    @staticmethod
    def get_fio(obj):
        return obj.__str__()
