import stripe
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def total_items_in_cart(request):
    cart = Cart.objects.filter(user=request.user)
    total_items = len(cart)
    return total_items


class HomeView(View):
    def get(self, request, *args, **kwargs):
        totalitems = total_items_in_cart(request)
        return render(request, 'shop/home.html', locals())


class ShopView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        cart = Cart.objects.filter(user=request.user)
        cart_list = []
        for item in cart:
            cart_list.append(item.product.title)
        totalitems = total_items_in_cart(request)
        return render(request, 'shop/shop.html', locals())


class ShopCatView(View):
    def get(self, request, cat, *args, **kwargs):
        products = Product.objects.filter(category=cat)
        cart = Cart.objects.filter(user=request.user)
        cart_list = []
        for item in cart:
            cart_list.append(item.product.title)
        totalitems = total_items_in_cart(request)
        return render(request, 'shop/shop.html', locals())


def add_to_cart(request):
    if request.method == 'GET':
        product_id = request.GET['prod_id']
        product = Product.objects.get(pk=product_id)
        if not Cart.objects.filter(Q(user=request.user) & Q(product=product)):
            product_in_cart = Cart(user=request.user, product=product)
            product_in_cart.save()
            data = {}
        return JsonResponse(data)


def remove_from_cart(request):
    if request.method == 'GET':
        product_id = request.GET['prod_id']
        product = Product.objects.get(pk=product_id)
        if Cart.objects.filter(Q(user=request.user) & Q(product=product)):
            Cart.objects.filter(Q(user=request.user) & Q(product=product)).delete()
            data = {}
        return JsonResponse(data)


class CartView(View):
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        totalitems = total_items_in_cart(request)
        total_price_str = ''
        totalprice = 0

        products_id = ''
        for item in cart:
            totalprice += float(item.get_full_price())
            total_price_str = '{0:.2f}'.format(totalprice)
            products_id += str(item.product.pk) + '-'

        STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
        return render(request, 'shop/cart.html', locals())


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        products_id = self.kwargs['list']

        products_id_list = []
        for item in products_id:
            if item == '-':
                continue
            else:
                products_id_list.append(item)

        products_in_cart = Cart.objects.filter(user=request.user, product__pk__in=products_id_list)

        if settings.DEBUG:
            YOUR_DOMAIN = 'http://127.0.0.1:8000'

        sum_price = 0
        products_name = ''
        for item in products_in_cart:
            sum_price += item.get_int_price()
            products_name += item.product.title + " "

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': sum_price,
                        'product_data': {
                            'name': products_name,
                        }
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'products_id': 1
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/shop/',
            cancel_url=YOUR_DOMAIN + '/cart/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body

    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session['customer_details']['email']
        products_id = session['metadata']['products_id']

        product = Product.objects.filter(id__in=products_id)

        send_mail(
            subject='Here is your product',
            message=f'Thanks for your purchase. Here is the product you ordered.',
            recipient_list=[customer_email],
            from_email='nikitos.shorick@gmail.com'
        )

    return HttpResponse(status=200)


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(pk=prod_id)
        cart = Cart.objects.get(Q(user=request.user) & Q(product=product))
        cart.quantity += 1
        cart.save()
        data = {
            'quantity': cart.quantity
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(pk=prod_id)
        cart = Cart.objects.get(Q(user=request.user) & Q(product=product))
        if cart.quantity > 0 and cart.quantity != 0:
            cart.quantity -= 1
            cart.save()
            data = {
                'quantity': cart.quantity
            }
        return JsonResponse(data)