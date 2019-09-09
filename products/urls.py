from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('events/<int:event_id>/shop/',views.ShopView.as_view(), name='shop'),
    path('ajax/add_cart_simple/', views.addSimpleProduct, name='add_cart_simple'),
    #path('ajax/add_cart_complex/', views.addTicket, name='add_ticket'),
]
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
