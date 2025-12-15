from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from ..models import Users, Carts, CartItems, Products

def get_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = Users.objects.get(id=user_id)
        cart = Carts.objects.get(user=user)
        items = CartItems.objects.filter(cart=cart)
        # Tính tổng tiền
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
    if request.method != 'POST':
        return JsonResponse({'status': 'fail', 'message': 'Yêu cầu không hợp lệ'})

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Vui lòng đăng nhập để mua hàng!'})

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Người dùng không tồn tại!'})

    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    # Tìm hoặc tạo giỏ hàng
    user_cart, created = Carts.objects.get_or_create(user=user, defaults={'created_at': timezone.now()})

    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại!'})

    # Thêm sản phẩm vào chi tiết giỏ
    cart_item, created = CartItems.objects.get_or_create(
        cart=user_cart,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Tính tổng số lượng để update icon
    items_in_cart = CartItems.objects.filter(cart=user_cart)
    total_quantity = sum(item.quantity for item in items_in_cart)

    return JsonResponse({'status': 'success', 'total_quantity': total_quantity})

def get_payment(request):
    return render(request, 'main/payment.html')