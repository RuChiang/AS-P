from django.shortcuts import render
from django.views.generic.list import ListView
from asp.models import Item, Order, Ordered_Item, UserExt, Hospital
from django.http import HttpResponse
from django.utils import timezone
from asp.forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# Create your views here.

def logout_view(request):
    logout(request)
    return HttpResponse("logged out!!")

def login_view(request):
    #  if it is post, it means user is logging in
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # try to create a user here

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse("logged in!!")
            else:
                return HttpResponse("No such user")

        # form not valid, sign in again
        else:
            return HttpResponse("wrong" + str(form.errors))

    #  a get method means the user want the form
    elif request.method == 'GET':
        form = LoginForm()
        return render(request, 'asp/login.html', {'form':form})
    # # dunno which HTTP method its using
    else:
        return HttpResponse("how did you even got here?")



def signup_view(request):
    #  if it is post, it means user is signing up
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # try to create a user here
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save()
            userExt = UserExt(
                user = user,
                hospital = Hospital.objects.get(name = form.cleaned_data['hospital']),
                role = form.cleaned_data['role']
            )
            userExt.save()
            login(request, user)
            return HttpResponse("signed up successfully. The system has logged you in as well")
        else:
            return HttpResponse("wrong" + str(form.errors))
    #  a get method means the user want the form
    elif request.method == 'GET':
        form = SignupForm()
        return render(request, 'asp/signup.html', {'form':form})
    # # dunno which HTTP method its using
    else:
        return HttpResponse("how did you even got here?")


class ItemsViewAll(ListView):
    model = Item

def marketPlace(request):
    category
    items = Item.objects.filter(supplying_hospital = UserExt.objects.filter(user = request.user)[0].hospital)
    return render(request, 'asp/marketplace.html', {'item_list':items})

def placeOrder(request):
    weight_limit = 23.8
    items = Item.objects.filter(supplying_hospital = UserExt.objects.filter(user = request.user)[0].hospital)
    orders_items = {}
    if request.method == 'GET':
        # see if this is simply routing
        if len(request.GET) == 0:
            return render(request, 'asp/marketplace.html', {'item_list':items })
        in_stock = True
        # extract the order details into the order dict
        req_priority = 1
        for item in request.GET:
            if item != 'priority':
                orders_items[str(item)] = int(request.GET[item])
            else:
                if request.GET[item] == 'low':
                    req_priority = 1
                elif request.GET[item] == 'medium':
                    req_priority = 2
                elif request.GET[item] == 'high':
                    req_priority = 3

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

        Order_model = Order(status='QFP', requester = UserExt.objects.filter(user = request.user)[0] , time=timezone.now(), priority=req_priority)
        Order_model.save()

        # create an order, and subtract the quantity of the available supplies
        OrderedItem_models = []
        for orders_item in orders_items:
            item_in_db = Item.objects.get(name=str(orders_item))
            item_in_db.quantity = item_in_db.quantity - orders_items[orders_item]
            item_in_db.save()
            new_ordered_item = Ordered_Item(item = str(orders_item), quantity = orders_items[orders_item], order = Order_model)
            new_ordered_item.save()
            OrderedItem_models.append(new_ordered_item)

        # think about how to relate to the requester
        # add a field for the priority
        # are there other ways to simplify this logic?


        msg = "order successfully placed"
        return render(request, 'asp/marketplace.html', {'success':msg, 'item_list':items })


    else:
        return HttpResponse("requested with invalid method")
