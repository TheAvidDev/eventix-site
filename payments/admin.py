from django.contrib import admin
from .models import *

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0

class TicketAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_price', 'get_status', 'customerName', 'referral', 'status')
    list_editable = ('status','customerName','referral')

class RowAdmin(admin.ModelAdmin):
    inlines = [ TicketInline, ]
    list_display = ('__str__', 'shortName', 'event', 'sortIndex')
    list_editable = ('shortName','sortIndex', 'event')

class ApparelSizeInline(admin.TabularInline):
    model = ApparelSize
    extra = 0

class ApparelAdmin(admin.ModelAdmin):
    inlines = [ ApparelSizeInline, ]

# Register your models here.
admin.site.register(Apparel, ApparelAdmin)
admin.site.register(ExtraTicket)
admin.site.register(Product)
admin.site.register(Row, RowAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Event)

admin.site.site_header = "Eventix Administration Page";
admin.site.site_title = "Eventix";
