from django.shortcuts import render
from django.views.generic.list import ListView
from asp.models import Item, Order, Ordered_Item, User
from django.http import HttpResponse
from django.utils import timezone
from asp.forms import SignupForm

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # try to create a user here
            '''
            TO BE DONE
            '''

class ItemsViewAll(ListView):
    model = Item

def marketPlace(request):
    items = Item.objects.get()
    return render(request, 'asp/marketplace.html', {'item_list':items})

def placeOrder(request):
    weight_limit = 23.8
    items = Item.objects.all()
    orders_items = {}
    if request.method == 'GET':
        in_stock = True
        # extract the order details into the order dict
        for item in request.GET:
            if item != 'priority':
                orders_items[str(item)] = int(request.GET[item])
            else:
                if request.GET[item] == 'low':
                    priority = 1
                elif request.GET[item] == 'medium':
                    priority = 2
                elif request.GET[item] == 'high':
                    priority = 3

        for orders_item in orders_items:
            # check if the stock is enough
            if orders_items[orders_item] > int(Item.objects.get(name=str(orders_item)).quantity):
                msg = "no enough stock in " + str(orders_item) + " please place your order again"
                return render(request, 'asp/marketplace.html', {'err':msg, 'item_list':items })
        # no order placed and click placeOrder
        all_zero_order =  True if 0 not in orders_items.values() else False
        if not all_zero_order:
            msg = "Please input values for those supplies which you would like to order"
            return render(request, 'asp/marketplace.html', {'warning':msg, 'item_list':items })

        # create an order, and subtract the quantity of the available supplies
        OrderedItem_models = []
        for orders_item in orders_items:
            item_in_db = Item.objects.get(name=str(orders_item))
            item_in_db.quantity = item_in_db.quantity - orders_items[orders_item]
            item_in_db.save()
            new_ordered_item = Ordered_Item(item = str(orders_item), quantity = orders_items[orders_item])
            new_ordered_item.save()
            OrderedItem_models.append(new_ordered_item)

        # think about how to relate to the requester
        # add a field for the priority
        # are there other ways to simplify this logic?
        Order_model = Order(status='QFP', requester = User.objects.all()[0] , time=timezone.now(), priority=priority)
        Order_model.save()
        for OrderedItem_model in OrderedItem_models:
            Order_model.items.add(OrderedItem_model)
        Order_model.save()

        msg = "order successfully placed"
        return render(request, 'asp/marketplace.html', {'success':msg, 'item_list':items })


    else:
        return HttpResponse("requested with invalid method")
