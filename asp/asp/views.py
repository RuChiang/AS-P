from django.shortcuts import render
from django.views.generic.list import ListView
from asp.models import Item, Order
from django.http import HttpResponse

# Create your views here.

class ItemsViewAll(ListView):
    model = Item
