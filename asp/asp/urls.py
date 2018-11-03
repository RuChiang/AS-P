from django.urls import path
from asp import views


urlpatterns = [
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('self', views.UserViewSelf, name='self'),
    path('marketplace', views.marketPlace, name='marketplace'),
    path('login', views.loginView, name='login'),
    path('signup', views.signupView, name='signup'),
    path('logout', views.logoutView, name='logout'),
    path('viewDispatch', views.viewDispatch, name='viewDispatch'),
]
