from django.contrib import admin
from .models import UserExt, Item, Order, Ordered_Item, Hospital, Distance
# Register your models here.


admin.site.register(UserExt)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Ordered_Item)
admin.site.register(Hospital)
admin.site.register(Distance)
