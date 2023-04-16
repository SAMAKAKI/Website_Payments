from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('shop/', ShopView.as_view(), name="shop"),
    path('shop/<slug:cat>/', ShopCatView.as_view(), name="shop-cat"),
    path('cart/', CartView.as_view(), name="cart"),
    path('create-checkout-session/<slug:list>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/', remove_from_cart, name='remove-from-cart'),
    path('plus-cart/', plus_cart, name='plus_cart'),
    path('minus-cart/', minus_cart, name='minus_cart'),
]
