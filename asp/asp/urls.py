from django.urls import path
from asp import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    # gernerl user routes
    path('login', views.loginView, name='login'),
    path('signup/<str:encrypted_pk>', views.signupView, name='signup'),
    path('logout', views.logoutView, name='logout'),
    path('forgotPassword', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/<str:encrypted_pk>', views.resetPassword, name='resetPassword'),
    path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.activate, name='activate'),

    # debugging routes
    path('items', views.ItemsViewAll.as_view(), name='items'),
    path('self', views.UserViewSelf, name='self'),

    # clinic manager routes
    path('marketplace', views.marketPlace, name='marketplace'),

    # dispatcher routes
    path('viewDispatch', views.viewDispatch, name='viewDispatch'),
    path('downloadItinerary', views.downloadItinerary, name='downloadItinerary'),

    # warehouse routes
    path('downloadShippingLabel', views.downloadShippingLabel, name='downloadShippingLabel'),
    path('delivery', views.delivery, name='delivery'),
    path('viewWarehouse', views.viewWarehouse, name='viewWarehouse'),
    path('viewWarehouseProcessing', views.viewWarehouseProcessing, name='viewWarehouseProcessing'),

    # admin routes
    path('addUser', views.addUser, name='addUser'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
