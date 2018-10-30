from django.urls import path
from asp import views


urlpatterns = [
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('marketplace', views.marketPlace, name='marketplace'),
    path('placeOrder', views.placeOrder, name='placeOrder'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),


]
