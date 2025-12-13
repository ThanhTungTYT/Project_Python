from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import *

# --- CÁC VIEW HIỂN THỊ TRANG TĨNH (Giữ nguyên) ---
def get_shippingPolicies(request):
    return render(request, 'main/shippingPolicies.html')

def get_termOfUse(request):
    return render(request, 'main/termOfUse.html')

def get_warrantyPolicies(request):
    return render(request, 'main/warrantyPolicies.html')

def get_help(request):
    return render(request, 'main/help.html')

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

def get_about(request):
    return render(request, 'main/aboutUs.html')

def get_account(request):
    return render(request, 'main/account.html')

def get_info(request):
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)
    return render(request, 'main/info.html', {'user': user})

def get_changepw(request):
    return render(request, 'main/changepw.html')

def get_history(request):
    return render(request, 'main/history.html')

def get_register(request):
    if request.method == 'POST':
        yourname = request.POST.get('yourname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp!")
            return render(request, 'main/register.html')

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được sử dụng!")
            return render(request, 'main/register.html')

        try:
            new_user = Users(
                full_name=yourname,
                email=email,
                phone=phone,
                password_hash=make_password(password),
                role='customer'
            )
            new_user.save()

            # Tạo cart cho user mới
            Carts.objects.create(user=new_user, created_at=timezone.now())

            return redirect('login')

        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {e}")
            return render(request, 'main/register.html')
    return render(request, 'main/register.html')


def get_login(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            user = Users.objects.get(email=email_input)

            if check_password(password_input, user.password_hash):
                
                request.session['user_id'] = user.id
                request.session['user_name'] = user.full_name
                request.session.set_expiry(3600)

                return redirect('index')
            else:
                messages.error(request, "Sai mật khẩu!")

        except Users.DoesNotExist:
            messages.error(request, "Email chưa được đăng ký!")
    return render(request, 'main/login.html')
def get_logout(request):
    request.session.flush()
    return redirect('index')

def get_info(request):
    user_id = request.session.get('user_id')

    try:
        current_user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return render(request, 'main/info.html')
    context = {
        'user': current_user 
    }
    return render(request, 'main/info.html', context)

def get_index(request):
    products = Products.objects.all().order_by('-sold')[:4]
    context = {
        'products': products
    }
    return render(request, 'main/index.html', context)

def get_catalog(request):
    categories = Categories.objects.all()

    products = Products.objects.all()
    active_category = request.GET.get('category')
    
    if active_category:
        products = products.filter(category_id=active_category)
    active_sort = request.GET.get('sort')

    if active_sort == 'price_desc':
        products = products.order_by('-price')
    elif active_sort == 'price_asc':
        products = products.order_by('price')
    elif active_sort == 'sold':
        products = products.order_by('-sold')
    elif active_sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    context = {
        'products': products,    
        'categories': categories,  
        'active_category': active_category,
        'active_sort': active_sort      
    }
    
    return render(request, 'main/catalog.html', context)

def get_product(request, product_id):
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return redirect('catalog')
    
    related_products = Products.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:4]

    context = {
        'product': product,
        'related_products': related_products
    }

    return render(request, 'main/product.html', context)

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

    # Lấy hoặc tạo cart của user
    user_cart, created = Carts.objects.get_or_create(user=user, defaults={'created_at': timezone.now()})

    # Kiểm tra sản phẩm
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sản phẩm không tồn tại!'})

    # Lấy hoặc tạo CartItem
    cart_item, created = CartItems.objects.get_or_create(
        cart=user_cart,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Tính tổng số lượng
    items_in_cart = CartItems.objects.filter(cart=user_cart)
    total_quantity = sum(item.quantity for item in items_in_cart)

    return JsonResponse({'status': 'success', 'total_quantity': total_quantity})


def get_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = Users.objects.get(id=user_id)
        cart = Carts.objects.get(user=user)
        items = CartItems.objects.filter(cart=cart)
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






