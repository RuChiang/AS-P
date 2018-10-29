from django.shortcuts import render
from django.views.generic.list import ListView
from asp.models import Item, Order
from django.http import HttpResponse
from django.utils import timezone

# Create your views here.

class ItemsViewAll(ListView):
    model = Item

def marketPlace(request):
    items = Item.objects.all()
    return render(request, 'asp/marketplace.html', {'item_list':items})

def placeOrder(request):
    weight_limit = 23.8
    items = Item.objects.all()
    orders = {}
    if request.method == 'GET':
        in_stock = True
        # extract the order details into the order dict
        for item in request.GET:
            order[str(item)] = request.GET[item]
            # check if the stock is enough
            if int(orders[str(item)]) > int(Item.objects.get(name=str(item)).quantity):
                msg = "no enough stock in " + str(item) + " please place your order again"
                return render(request, 'asp/marketplace.html', {'err':msg, 'item_list':items })
        # no order placed and click placeOrder
        all_zero_order =  True if 0 not in orders.values() else False
        if all_zero_order:
            msg = "Please input values for those supplies which you would like to order"
            return render(request, 'asp/marketplace.html', {'warning':msg, 'item_list':items })

        # create an order
        OrderedItem_models = []
        for order, quant in orders:
            OrderedItem_models.append(Ordered_Item(item = order, quantity = quant))
        # think about how to relate to the requester
        # add a field for the priority
        # are there other ways to simplify this logic?
        Order_model = Order(status='QFP', requester = , time=timezone.now(), priority)
        Order_model.save()
        for OrderedItem_model in OrderedItem_models:
            Order_model.items.add(OrderedItem_model)
        Order_model.save()

        msg = "order successfully placed"
        return render(request, 'asp/marketplace.html', {'success':msg, 'item_list':items })


    else:
        return HttpResponse("requested with invalid method")
