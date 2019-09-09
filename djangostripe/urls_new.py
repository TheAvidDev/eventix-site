#Main urls.py for all app control
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('payments.urls')), #new
    path('', include('events.urls')), #new
    #path('', include('products.urls')), #new
]
