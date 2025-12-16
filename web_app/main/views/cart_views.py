from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..models import Users, Carts, CartItems, Products

def get_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'main/login.html')

    try:
        user = Users.objects.get(id=user_id)
        cart = Carts.objects.get(user=user)
        items = CartItems.objects.filter(cart=cart).order_by('-id')
        total_price = sum(item.product.price * item.quantity for item in items)
    except (Users.DoesNotExist, Carts.DoesNotExist):
        cart = None
        items = []
        total_price = 0

    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price
    }
    return render(request, 'main/cart.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Vui lòng đăng nhập để mua hàng!")
            return redirect('login')

        product_id = request.POST.get('product_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        try:
            user = Users.objects.get(id=user_id)
            user_cart, _ = Carts.objects.get_or_create(
                user=user, 
                defaults={'created_at': timezone.now()}
            )

            product = Products.objects.get(id=product_id)
        
            cart_item, created = CartItems.objects.get_or_create(
                cart=user_cart, 
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
        except (Users.DoesNotExist, Products.DoesNotExist) as e:
            e.print(e)

    return redirect('cart')

def remove_cart_item(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')

        cart_item_id = request.POST.get('cart_item_id')

        try:
            cart_item = CartItems.objects.get(id=cart_item_id, cart__user_id=user_id)
            cart_item.delete()
        except CartItems.DoesNotExist:
            pass

    return redirect('cart')

def remove_all_cart_items(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')

        try:
            cart = Carts.objects.get(user_id=user_id)
            CartItems.objects.filter(cart=cart).delete()
        except Carts.DoesNotExist:
            pass

    return redirect('cart')

def get_payment(request):
    return render(request, 'main/payment.html')