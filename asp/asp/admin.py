from django.contrib import admin
from .models import UserExt, Item, Order, Ordered_Item, Hospital, Distance, Category, Available_Item
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

class UserExtInline(admin.StackedInline):
    model = UserExt
    can_delete = False
    verbose_name_plural = 'UserExt'

# class ClinicManagerInline(admin.StackedInline):
#     model = ClinicManager
#     can_delete = False
#     verbose_name_plural = 'ClinicManager'
#
# class WarehousePersonnelInline(admin.StackedInline):
#     model = WarehousePeronnel
#     can_delete = False
#     verbose_name_plural = 'WarehousePeronnel'
#
# class DispatcherInline(admin.StackedInline):
#     model = Dispatcher
#     can_delete = False
#     verbose_name_plural = 'Dispatcher'


class UserAdmin(UserAdmin):
    inlines = (UserExtInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Ordered_Item)
admin.site.register(Hospital)
admin.site.register(Distance)
admin.site.register(Category)
admin.site.register(Available_Item)
