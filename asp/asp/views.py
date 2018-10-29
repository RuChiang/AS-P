from django.shortcuts import render
from django.views.generic.list import ListView
from asp.models import Item, Order
from django.http import HttpResponse

# Create your views here.

class ItemsViewAll(ListView):
    model = Item

def marketPlace(request):
    items = Item.objects.all()
    return render(request, 'asp/marketplace.html', {'item_list' : items, 'weight_limit' : 23.8})
