from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('charge/', views.ChargeView.as_view(), name='charge'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('ajax/add_ticket/', views.addTicket, name='add_ticket'),
    path('events/<int:event_id>/tickets/', views.TicketView.as_view(), name='tickets'),
    path('events/<int:event_id>/shop/',views.ShopView.as_view(), name='shop'),
    path('ajax/add_cart_simple/', views.addProduct, name='add_cart_simple'),
    #path('ajax/add_cart_complex/', views.addTicket, name='add_ticket'),
    path('',views.EventPageView.as_view(), name='events'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
