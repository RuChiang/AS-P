from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from asp.models import Item, Order, Ordered_Item, UserExt, Hospital, Available_Item
from django.http import HttpResponse
from django.utils import timezone
from asp.forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from asp import utils
import os


# Create your views here.

def downloadItinerary(request):
    file = open('asp/static/asp/itinerary.csv', 'rb')
    response = HttpResponse(content=file,content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="itinerary.csv"'
    return response


def logoutView(request):
    logout(request)
    return HttpResponse("logged out!!")

def loginView(request):
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

def signupView(request):
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
                supplying_hospital = Hospital.objects.get(name = form.cleaned_data['supplying_hospital']),
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
    model = Available_Item

def UserViewSelf(request):
    user = request.user
    userext = UserExt.objects.get(user = request.user)
    items = []
    items.append(user.username)
    items.append(user.email)
    items.append(userext.hospital.name)
    items.append(userext.role)
    # print(items)
    return render(request, 'asp/user_show_self.html', {'item_list':items})

# def marketPlace(request):
#     # items = Item.objects.filter(supplying_hospital = UserExt.objects.filter(user = request.user)[0].hospital)
#     items = utils.arrange_items_by_category(request.user)
#     return render(request, 'asp/marketplace.html', {'item_list':items})
def marketPlace(request):
    weight_limit = 23.8
    # items = Item.objects.filter(supplying_hospital = UserExt.objects.filter(user = request.user)[0].hospital)
    items = utils.arrange_items_by_category(request.user)
    orders_items = {}
    if request.method == 'GET':
        # see if this is simply routing
        if len(request.GET) == 0:
            return render(request, 'asp/marketplace.html', {'item_list':items })
        # extract the order details into the order dict
        req_priority = 1
        for item in request.GET:
            if item != 'priority':
                orders_items[str(item)] = int(request.GET[item])
            else:
                req_priority = utils.transform_priority_to_integer(request.GET[item])

        for orders_item in orders_items:
            orders_item_abstract = Item.objects.get(name = str(orders_item))
            orders_item_supplying_hospital = UserExt.objects.get(user = request.user).supplying_hospital
            if not Available_Item.objects.get(item_abstract = orders_item_abstract,
                supplying_hospital = orders_item_supplying_hospital
                ).is_enough(orders_items[orders_item]):
                msg = "no enough stock in " + str(orders_item) + " please place your order again"
                return render(request, 'asp/marketplace.html', {'err':msg, 'item_list':items })
        # no order placed and click placeOrder
        all_zero_order =  True if all(v == 0 for v in orders_items.values()) else False
        if all_zero_order:
            msg = "Please input values for those supplies which you would like to order"
            return render(request, 'asp/marketplace.html', {'warning':msg, 'item_list':items })

        Order_model = Order(status='QFP', requester = UserExt.objects.get(user = request.user) , time_queued_processing=timezone.now(), priority=req_priority)
        Order_model.save()

        # create an ordered_item, and subtract the quantity of the available supplies
        for orders_item in orders_items:
            if orders_items[orders_item] != 0:
                item_in_db = Available_Item.objects.get(supplying_hospital = UserExt.objects.get(user = request.user).supplying_hospital, item_abstract = Item.objects.get(name = str(orders_item)))
                item_in_db.quantity = item_in_db.quantity - orders_items[orders_item]
                item_in_db.save()
                new_ordered_item = Ordered_Item(item = Item.objects.get(name = str(orders_item)), quantity = orders_items[orders_item], order = Order_model)
                new_ordered_item.save()

        # think about how to relate to the requester
        # add a field for the priority
        # are there other ways to simplify this logic?


        msg = f"order successfully placed. Order id is, {Order_model.id}"
        return render(request, 'asp/marketplace.html', {'success':msg, 'item_list':items })


    else:
        return HttpResponse("requested with invalid method")

def viewDispatch(request):
    ordersToDispatch = Order.objects.filter(status = 'QFD').order_by('-priority', 'time_queued_processing')
    # Only happens after one group was already dispatched
    if request.method == 'POST':
        count = int(request.POST.get("count"))
        i = 0
        # Change to dispatched
        for order in ordersToDispatch:
            order.status = 'DSD'
            order.time_dispatched = timezone.now()
            order.save()
            i+=1
            if i == count:
                break
        # Refresh to not have a POST method in request
        return redirect('/asp/viewDispatch')
    # when simply accessing this route
    else:
        weightLimit = 23.8
        count = 0
        sumWeight = 0.0
        '''
        ityHospitals list containes all the hospitals to which the supplies are delivered
        the last element is the hospital that is dispatching all the ordered items
        '''
        ityHospitals = []
        if len(ordersToDispatch) >= 1:
            for order in ordersToDispatch:
                # For checking how many orders to group together
                sumWeight += order.getTotalWeight()
                # For finding the corresponding clinic of the order
                ityHospitals.append(UserExt.objects.get(id = order.requester.id).hospital)
                # Weight limit exceeded, don't count anymore
                if sumWeight > weightLimit:
                    break
                count += 1

            supply_hospital = utils.getSupplyingHospital(order)
            # put the supply_hospital at the end of the list
            ityHospitals.append(supply_hospital)
            vertices = list()
            for x in ityHospitals:
                if x not in vertices:
                    vertices.append(x)
            itinerary = utils.generateItinerary(vertices)
            path_to_file = utils.generateCSV(itinerary)
        return render(request, 'asp/dispatch.html', {'orders' : ordersToDispatch[:count], 'count': count})
