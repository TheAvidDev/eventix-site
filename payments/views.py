import stripe
import time

from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone

from django.db import transaction, DatabaseError

from .models import *


stripe.api_key = settings.STRIPE_SECRET_KEY

class EventPageView(TemplateView):
    template_name = 'events.html'

    def get_context_data(self, **kwargs):
        self.request.session['referral'] = self.request.GET.get('r', '')

        #Remove empty rows
        finalevents = []
        events = Event.objects.all().order_by('-date')
        for event in events:
            if (event.date > timezone.now()):
                finalevents.append(event)

        #Add rows to context
        context = super().get_context_data(**kwargs)
        context['events'] = finalevents
        return context

def privacypolicy(request):
    return render(request,'privacypolicy.html')

class ShopView(TemplateView):
    template_name = 'shop.html'

    def get_context_data(self, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])

        context = super().get_context_data(**kwargs)
        context['products'] = event.products.all()
        context['apparels'] = event.apparels.all()
        context['extra_tickets'] = event.extra_tickets.all()
        return context

#Add tickets for Checkout button
def addProduct(request):
    if request.method == 'POST':
        print(request.POST.getlist('data[]'))
        #Organize Tickets
        product_pk = request.POST.get('pk')

        request.session['simple_cart_pks'] = product_pk
        #Return redirect
        data = {
        'redirect':'/checkout/'
        }
        return JsonResponse(data)
    else:
        return redirect('/')

class TicketView(TemplateView):
    template_name = 'tickets.html'

    def get_context_data(self, **kwargs):

        event = get_object_or_404(Event, pk=self.kwargs['event_id'])

        #Manage sessions
        try_delete_all(self.request)

        #Remove empty rows
        finalrow = []
        rows = event.rows.all().order_by('-sortIndex').reverse()
        for row in rows:
            if len(row.seats.filter(status=1)) != 0:
                finalrow.append(row)

        #Add rows to context
        context = super().get_context_data(**kwargs)
        context['rows'] = finalrow
        context['event'] = event
        return context

class CheckoutView(TemplateView):
    template_name = 'checkout.html'

    def get(self, request):
        if request.session.get('tickets') == None:
            return redirect('/')
        else:
            return super(CheckoutView, self).get(request)

    def get_context_data(self, **kwargs):
        pks = self.request.session.get('tickets')
        total = self.request.session.get('total')
        price = self.request.session.get('stripe_price')
        fee = self.request.session.get('fee')

        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['tickets'] = Ticket.objects.filter(pk__in=pks)
        context['total'] = total
        context['price'] = price
        context['fee'] = fee
        return context

class ChargeView(TemplateView):
    template_name = 'charge.html'

    #@transaction.atomic
    def post(self, request):
        stripe_price = self.request.session.get('stripe_price')
        pks = self.request.session.get('tickets')
        tickets = Ticket.objects.filter(pk__in=pks)

        #Event name get
        event_name = tickets[0].row.event.name

        #List of tickets for receipt
        output_tickets='\n'
        for ticket in tickets:
            output_tickets += ticket.row.name[-1:] + str(ticket.seatNum) + ', '
        output_tickets=output_tickets[:-2]

        #Set ticket to unavailable
        tickets = Ticket.objects.select_for_update(nowait=True).filter(pk__in=pks)
        try:
            with transaction.atomic():
                for ticket in tickets:
                    if (ticket.status == 1):
                        ticket.referral = request.session.get('referral')
                        ticket.customerName = request.POST['name']
                        ticket.status = 2
                        ticket.save()
                    else:
                        return redirect('/charge?type=fail');
        except DatabaseError as e:
            return redirect('/charge?type=fail')

        try:
            #Customer creation based off email
            customer = stripe.Customer.create(
            email = request.POST['email'],
            source=request.POST['stripeToken'],
            )

            #Charge generation
            charge = stripe.Charge.create(
            customer = customer.id,
            amount = stripe_price,
            currency = 'cad',
            description=event_name + ' Seats: ' + output_tickets,
            receipt_email=request.POST['email'],
            metadata = {'ticket_pks':str(pks)},
            )



            print('redirecting')
            return redirect('/charge?type=success&id=' + charge.id[-6:])
            pass

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body.get('error', {})

            print("Status is: %s" % e.http_status)
            print("Type is: %s" % err.get('type'))
            print("Code is: %s" % err.get('code'))
            # param is '' in this case
            print("Param is: %s" % err.get('param'))
            print("Message is: %s" % err.get('message'))

            return redirect('/charge?type=carderror')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            print('RateLimitError e')
            return redirect('/charge?type=errorslow')

            pass
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print('InvalidRequestError e')
            return redirect('/charge?type=error')

            pass
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print('AuthenticationError e')
            return redirect('/charge?type=error')

            pass
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            print('ApiConnnectionError e')
            return redirect('/charge?type=error')

            pass
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print('StripeError e')
            return redirect('/charge?type=error')

            pass

    def get_context_data(self, **kwargs):
        type = self.request.GET.get('type', '')
        id = self.request.GET.get('id', '')

        context = super().get_context_data(**kwargs)

        pks = self.request.session.get('tickets')
        total = self.request.session.get('total')
        fee = self.request.session.get('fee')

        if ((pks != None) & (total!= None) & (fee != None)):
            context['tickets'] = Ticket.objects.filter(pk__in=pks)
            context['total'] = total
            context['type'] = type
            context['id'] = id
            context['fee'] = fee

        else:
            context['type'] = 'error'

        #Manage sessions
        try_delete_all(self.request)
        return context

#Add tickets for Checkout button
def addTicket(request):
    if request.method == 'POST':
        #Organize Tickets
        tickets = request.POST.get('tickets')
        tickets = tickets.split(' ')
        del tickets[0]
        pks = list(map(int, tickets))

        #Calculate total & stripe price
        total_price = 0
        for ticket_pk in pks:
            total_price += Ticket.objects.get(pk=ticket_pk).price


        fee = round((total_price+0.3)/0.971-total_price,2)
        total_price += fee
        stripe_price = int(round(total_price*100))
        total_price = "%01.2f" % total_price

        #Manage sessions
        try_delete_all(request)

        request.session['tickets'] = pks
        request.session['total'] = total_price
        request.session['stripe_price'] = stripe_price
        request.session['fee'] = fee

        #Return redirect
        data = {
        'redirect':'/checkout/'
        }
        return JsonResponse(data)
    else:
        return redirect('/')

#Helper functions to remove session items
def try_delete(request, name):
    try:
        del request.session[name]
    except KeyError:
        pass

def try_delete_all(request):
    try_delete(request, 'tickets')
    try_delete(request, 'total')
    try_delete(request, 'stripe_price')
    try_delete(request, 'fee')
