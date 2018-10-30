from django.urls import path
from asp import views


urlpatterns = [
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('marketplace', views.marketPlace, name='marketplace'),
    path('placeOrder', views.placeOrder, name='placeOrder'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='signup'),
    path('logout', views.logout_view, name='logout'),



]
