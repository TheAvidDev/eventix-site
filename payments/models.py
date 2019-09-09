from django.utils import timezone
import datetime
from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=300, default='')
    description = models.CharField(max_length=2000, default='')
    location = models.CharField(max_length=500, default='')
    date = models.DateTimeField(blank=True);
    eventurl = models.CharField(max_length=1000, default='', blank=True)
    image = models.ImageField(upload_to='logos/', blank=True)
    seatmap = models.ImageField(upload_to='seatmaps/', blank=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=300, default='')
    description = models.CharField(max_length=1000, default='')
    price = models.FloatField(default=100.00)
    stock = models.IntegerField(default=-1) #-1:Infinite/Pass to Sizing
    image = models.ImageField(upload_to='products/', blank=True)
    customerName = models.CharField(max_length=100, default='', blank=True)
    referral = models.CharField(max_length=100, default='', blank=True)
    event = models.ForeignKey(Event, related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name

class ExtraTicket(Product):
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=300, default='')
    event_child = models.ForeignKey(Event, related_name='extra_tickets', on_delete=models.CASCADE, blank=True, null=True)

class Apparel(Product):
    DELIVERY_METHODS = (
        (1, 'Pickup'),
        (2, 'Ship'),
    )
    deliveryMethod = models.IntegerField(default=1,choices=DELIVERY_METHODS)
    customerDeliveryLocation = models.CharField(max_length=300, default='', blank=True)
    event_child = models.ForeignKey(Event, related_name='apparels', on_delete=models.CASCADE, blank=True, null=True)

class ApparelSize(models.Model):
    SIZES = (
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    )
    size = models.CharField(max_length=3,default='L',choices=SIZES)
    stock = models.IntegerField(default='1')
    apparel = models.ForeignKey(Apparel, related_name='sizes', on_delete=models.CASCADE)

class Row(models.Model):
    name = models.CharField(max_length=300, default='Untitled Row')
    shortName = models.CharField(max_length=10, default='A')
    sortIndex = models.IntegerField()
    event = models.ForeignKey(Event, related_name='rows', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name

class Ticket(models.Model):
    seatNum = models.IntegerField(default=999)
    price = models.FloatField(default=100.00)
    status = models.IntegerField(default=1) #1-Available, 2-Bought
    customerName = models.CharField(max_length=100, default='', blank=True)
    referral = models.CharField(max_length=100, default='', blank=True)
    row = models.ForeignKey(Row, related_name='seats', on_delete=models.CASCADE)
    def get_status(self):
        if (self.status==1):
            return 'Available'
        elif (self.status==2):
            return 'Sold'
        else:
            return 'In-Progress'
    def get_name(self):
        return self.row.event.name + ' - Seat ' + self.row.shortName + ' ' + str(self.seatNum)
    def __str__(self):
        return self.row.name + ' - Ticket [' + str(self.seatNum) + ']'
    def get_price(self):
        return "%01.2f" % self.price
