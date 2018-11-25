from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from asp.models import Item, Order, Ordered_Item, UserExt, Hospital, Available_Item
from django.http import HttpResponse
from django.contrib.auth.models import Permission
from django.utils import timezone
from asp.forms import SignupForm, LoginForm, AddUser , GetPassword, ResetPassword, ClinicManagerSignupForm, ManageAccout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from asp import utils
import os
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from asp.tokens import account_creation_token
from django.utils.encoding import force_text
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage


from django.db.models import Q
# Create your views here.

def homePage(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    route = utils.redirect_to_homepage(request.user)
    return redirect(route)

def cancelOrder(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user = request.user).is_permitted_to_access('CM'):
        if request.method == 'POST':
            order_id = request.POST['Order_ID']
            order = Order.objects.get(id = order_id)
            order.delete()
        return redirect('viewAndTrackOrder')
    else:
        return HttpResponse('No Permission', status = 403)

def viewAndTrackOrder(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user = request.user).is_permitted_to_access('CM'):
        ordersNotYetDelivered = Order.objects.filter(Q(status = 'QFP') | Q(status = 'PBW') | Q(status = 'QFD') | Q(status = 'DSD')).filter(requester = UserExt.objects.get(user = request.user).id)
        return render(request, 'asp/view_and_track_order.html', {'orders': ordersNotYetDelivered})
    else:
        return HttpResponse('No Permission', status = 403)

def manageAccount(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if request.method == 'POST':
        form = ManageAccout(request.POST)
        if form.is_valid():
            for key in form.cleaned_data:
                if key != 'password':
                    if form.cleaned_data[key] != '':
                        print(f"setting the attr {key} from {getattr(request.user, key)} to {form.cleaned_data[key]}")
                        setattr(request.user, key, form.cleaned_data[key])
                else:
                    if form.cleaned_data['password'] != '':
                        request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            login(request, request.user)
        route = utils.redirect_to_homepage(request.user)
        return redirect(route)
    elif request.method == 'GET':
        form = ManageAccout()
        return render(request, 'asp/manage_account.html', {'form': form})
    else:
        return HttpResponse("how did you even got here?")


def downloadShippingLabel(request):
    order = Order.objects.get(id = int(request.GET['order_id']))
    shippingData = utils.generateShippingData(order)
    path_to_file = 'asp/media/shipping_labels/'
    filename = 'shipping_label_' + str(order.id) + '.pdf'
    utils.generateShippingLabel(path_to_file + filename, order,shippingData)
    file = open(path_to_file + filename, 'rb')
    response = HttpResponse(file,content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename={filename}"

    return response


def viewWarehouseProcessing(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user = request.user).is_permitted_to_access('WP'):
        if request.method=='GET':
            if len(request.GET) != 0:
                order_id = int(request.GET['order_id'])
                order = Order.objects.get(id=order_id)
                order.processing_by = request.user.pk
            else:
                order = Order.objects.get(processing_by=request.user.pk)
            order.status = 'PBW'
            order.time_processing = timezone.now()
            order.save()
            items = Ordered_Item.objects.filter(order_id=order.id)

        # DEBUG
        # for item in items:
            # print(item.item.name)
        return render(request, 'asp/warehouseProcessing.html', {'order_to_display': order, 'items': items})
    else:
        return HttpResponse('No Permission', status = 403)

def viewWarehouse(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user=request.user).is_permitted_to_access('WP'):
        #personnel = UserExt.objects.get(user=request.user)


        ordersToPickPack = Order.objects.filter(status='QFP').order_by('-priority', 'time_queued_processing')
        if request.method == 'GET':
            if len(request.GET) != 0:
                # update the status of the specified order to queue for dispatch
                order_id = int(request.GET['order_id'])
                order = Order.objects.get(id= order_id)
                order.status = 'QFD'
                order.processing_by=0
                order.time_queued_dispatch = timezone.now()
                order.save()
            else:
                haveOrdersToprocess = Order.objects.get(processing_by=request.user.pk)
                if haveOrdersToprocess:
                    return redirect('/asp/viewWarehouseProcessing')


            #TODO: order_to_pickpack will break if there is no item
        return render(request, 'asp/warehouse.html', {'orders': ordersToPickPack, 'first_order': (ordersToPickPack[0].id if len(ordersToPickPack) > 0 else -1) })
    else:
        return HttpResponse('No Permission', status = 403)

def delivery(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)

    if UserExt.objects.get(user = request.user).is_permitted_to_access('CM'):
        ordersToDeliver = Order.objects.filter(status = 'DSD').filter(requester = UserExt.objects.get(user = request.user).id)
        if request.method == 'POST':
            for item in request.POST:
                if item == "Order_ID":
                    order = Order.objects.get(id = int (request.POST[item]))
                    order.status = 'DLD'
                    order.time_delivered = timezone.now()
                    order.save()
            return redirect('/asp/delivery')
        return render(request, 'asp/delivery.html', {'orders': ordersToDeliver})
    else:
        return HttpResponse('No Permission', status = 403)

def downloadItinerary(request):
    file = open('asp/static/asp/itinerary.csv', 'rb')
    response = HttpResponse(content=file,content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="itinerary.csv"'
    return response

def logoutView(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(f"/asp/login")
    else:
        return HttpResponse("You are not even logged in")

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
                route = utils.redirect_to_homepage(user)
                return redirect(route)
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


def signupView(request, encrypted_pk):
    #  if it is post, it means user is signing up
    try:
        uid = urlsafe_base64_decode(encrypted_pk).decode()
        user = User.objects.get(pk=uid)
        userExt = UserExt.objects.get(user = user)
        role = userExt.role
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponse("No sneaking in here!!", status=403)

    if request.method == 'POST':
        if role == 'CM':
            form = ClinicManagerSignupForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                user.username = form.cleaned_data['username']
                user.set_password(form.cleaned_data['password'])
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                userExt.hospital = Hospital.objects.get(name = form.cleaned_data['hospital'])
                userExt.save()
                #login(request, user)
                #return HttpResponse("signed up successfully. The system has logged you in as well")
                return redirect(f"/asp/login")
            else:
                return HttpResponse("wrong" + str(form.errors))
        else:
            form = SignupForm(request.POST or None, request.FILES or None)
            if form.is_valid():
                user.username = form.cleaned_data['username']
                user.set_password(form.cleaned_data['password'])
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                userExt.hospital = Hospital.objects.get(name = 'Queen Mary Hospital Drone Port')
                userExt.save()
                # login(request, user)
                # return HttpResponse("signed up successfully. The system has logged you in as well")
                return redirect(f"/asp/login")
            else:
                return HttpResponse("wrong" + str(form.errors))
    #  a get method means the user want the form
    elif request.method == 'GET':
        # distinguish which form to send(Clinic manager needs the form speicifying the hospital)
        if role == 'CM':
            form = ClinicManagerSignupForm()
        else:
            form = SignupForm()
        return render(request, 'asp/signup.html', {'form':form, 'PK':encrypted_pk})
    # # dunno which HTTP method its using
    else:
        return HttpResponse("Getting here using neither POST nor GET")

def marketPlace(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user = request.user).is_permitted_to_access('CM'):

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
                    if (len(request.GET[item]) == 0):
                        itemQuantity = 0
                    else:
                        itemQuantity = int(request.GET[item])
                    orders_items[str(item)] = itemQuantity
                else:
                    req_priority = utils.transform_priority_to_integer(request.GET[item])

            for orders_item in orders_items:
                orders_item_abstract = Item.objects.get(name = str(orders_item))
                orders_item_supplying_hospital = UserExt.objects.get(user = request.user).hospital.supplying_hospital
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

            Order_model = Order(status='QFP', requester=UserExt.objects.get(user = request.user), time_queued_processing=timezone.now(), priority=req_priority)
            Order_model.save()

            # create an ordered_item, and subtract the quantity of the available supplies
            for orders_item in orders_items:
                if orders_items[orders_item] != 0:
                    item_in_db = Available_Item.objects.get(supplying_hospital = UserExt.objects.get(user = request.user).hospital.supplying_hospital, item_abstract = Item.objects.get(name = str(orders_item)))
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
    else:
        return HttpResponse('No Permission', status = 403)

def viewDispatch(request):
    if not request.user.is_authenticated:
        return HttpResponse('No Permission', status = 403)
    if UserExt.objects.get(user = request.user).is_permitted_to_access('DP'):
        ordersToDispatch = Order.objects.filter(status = 'QFD').order_by('-priority', 'time_queued_processing')
        destination_hospitals = []
        orders_to_dispatch_in_this_go = []
        if len(ordersToDispatch) > 0:
            weight_limit = 25
            sum_weight = 0.0

            for count, order in enumerate(ordersToDispatch):
                # 1.2 being the weight of the container
                if sum_weight + order.getTotalWeight() + 1.2 > weight_limit:
                    continue
                sum_weight += (order.getTotalWeight() + 1.2)
                destination_hospitals.append(UserExt.objects.get(id = order.requester.id).hospital)
                orders_to_dispatch_in_this_go.append(order)
            # print(f"sum weight {sum_weight}")
            # weird assumption: getting the supplying_hospital from anyone(the first in this case)
            # of the orders cuz it's the same for all of the orders
            destination_hospitals.append(Hospital.objects.get(name = utils.getSupplyingHospital(ordersToDispatch[0])))

            #check if the user click dispatch
            if request.method == 'POST':
                for order in orders_to_dispatch_in_this_go:
                    order.status = 'DSD'
                    order.time_dispatched = timezone.now()
                    order.save()
                    user = order.requester.user
                    mail_subject = 'Your Order has been dispatched'
                    message = render_to_string('order_dispatched_email.html', {
                        'user': user,
                    })
                    email = EmailMessage(
                        mail_subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                    )
                    email.attach_file(order.shipping_label_name)
                    email.send()
                return redirect('/asp/viewDispatch')

            vertices = list()
            for x in destination_hospitals:
                if x not in vertices:
                    vertices.append(x)
            # print(vertices)
            itinerary = utils.generateItinerary(vertices, orders_to_dispatch_in_this_go)
            path_to_file = utils.generateCSV(itinerary)

        return render(request, 'asp/dispatch.html', {'orders' : [ order for order in orders_to_dispatch_in_this_go if len(orders_to_dispatch_in_this_go) > 0 ]})
    else:
        return HttpResponse('No Permission', status = 403)

def addUser(request):
    if not request.user.is_superuser:
        return HttpResponse("no Permission", status = 403)
    if request.method == 'POST':
        form = AddUser(request.POST or None, request.FILES or None)
        if form.is_valid():
            # try to create a user here
            to_email = form.cleaned_data['email']
            user = User.objects.create_user(to_email,to_email,to_email)
            user.is_active = False
            # print(f"adding the user with id {user.pk}")
            user.save()
            profile = UserExt(
                user = user,
                # hospital = Hospital.objects.get(name = form.cleaned_data['hospital']),
                role = form.cleaned_data['role']
            )
            profile.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate Your Account'
            message = render_to_string('activate_account_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_creation_token.make_token(user),
            })
            # print(f"mail_subject: {mail_subject}\n message: {message}\nto_email: {to_email}")
            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [to_email],
            )
        return HttpResponse('Email token has been sent')
    else:
        form = AddUser()
    return render(request, 'asp/addUser.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponse('Can\'t find user')
    if account_creation_token.check_token(user, token):
        resetuser = UserExt.objects.get(user=user)
        # print(resetuser)
        # print(resetuser.resetPassword)
        if resetuser.resetPassword:
            resetuser.resetPassword = False
            resetuser.save()
            return redirect(f"/asp/resetPassword/{uidb64}")
        elif user.is_active == False :
            user.is_active = True
            user.save()
            return redirect(f"/asp/signup/{uidb64}")
        else:
            return HttpResponse("a bug to fix here on line 272 in view.py", status=404)
    else:
        return HttpResponse('Invalid token')

def forgotPassword(request):
    if(request.method == 'POST'):
        form = GetPassword(request.POST or None, request.FILES or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                resetuser = UserExt.objects.get(user=user)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                return HttpResponse('user not found', status=404)

            resetuser.resetPassword = True
            resetuser.save()
            # print(resetuser.resetPassword)
            current_site = get_current_site(request)
            mail_subject = 'Reset Password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_creation_token.make_token(user),
            })
            # print(f"mail_subject: {mail_subject}\n message: {message}\nto_email: {user.email}")
            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            return HttpResponse("Password reset email sent!")

        else:
            return HttpResponse("wrong" + str(form.errors))
    else:
        form = GetPassword()
    return render(request, 'asp/forgotPassword.html', {'form': form})


def resetPassword(request, encrypted_pk):
    try:
        uid = urlsafe_base64_decode(encrypted_pk).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponse("No sneaking in here!!", status=403)

    if request.method == 'POST':
        form = ResetPassword(request.POST or None, request.FILES or None)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            return  redirect("/asp/login")
        else:
            return HttpResponse("wrong" + str(form.errors))
    else:
        form = ResetPassword()
    return render(request, "asp/resetPassword.html", {'form':form, 'PK':encrypted_pk})


''' functions below are for debug uses '''
###########################################################

class ItemsViewAll(ListView):
    model = Available_Item

class OrdersViewAll(ListView):
    models = Order
    def get_queryset(self):
        return Order.objects.all()

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
