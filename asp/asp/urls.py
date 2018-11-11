from django.urls import path
from asp import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('self', views.UserViewSelf, name='self'),
    path('marketplace', views.marketPlace, name='marketplace'),
    path('login', views.loginView, name='login'),
    path('signup/<str:encrypted_pk>', views.signupView, name='signup'),
    path('logout', views.logoutView, name='logout'),
    path('viewDispatch', views.viewDispatch, name='viewDispatch'),
    path('downloadItinerary', views.downloadItinerary, name='downloadItinerary'),
    path('viewWarehouse', views.viewWarehouse, name='viewWarehouse'),
    path('addUser', views.addUser, name='addUser'),
    path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('forgotPassword', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/<str:encrypted_pk>', views.resetPassword, name='resetPassword'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
