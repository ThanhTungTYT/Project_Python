from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def get_index(request):
    return render(request, 'main/index.html')

def get_catalog(request):
    return render(request, 'main/catalog.html')

def get_cart(request):
    return render(request, 'main/cart.html')

def get_payment(request):
    return render(request, 'main/payment.html')

def get_login(request):
    return render(request, 'main/login.html')

def get_register(request):
    return render(request, 'main/register.html')