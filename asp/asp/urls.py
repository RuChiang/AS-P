from django.urls import path
from asp import views
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('self', views.UserViewSelf, name='self'),
    path('marketplace', views.marketPlace, name='marketplace'),
    path('login', views.loginView, name='login'),
    path('signup', views.signupView, name='signup'),
    path('logout', views.logoutView, name='logout'),
    path('viewDispatch', views.viewDispatch, name='viewDispatch'),
    path('downloadItinerary', views.downloadItinerary, name='downloadItinerary'),

]
