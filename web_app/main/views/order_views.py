from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from ..models import CartItems, Carts, OrderAddresses, OrderItems, Orders, PaymentMethod, Products, Promotions, Users

def prepare_checkout(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            messages.warning(request, "Bạn chưa chọn sản phẩm nào!")
            return redirect('cart')
        checkout_data = {}
        
        for p_id in selected_ids:
            qty_key = f"quantity_{p_id}" 
            qty = request.POST.get(qty_key, 1) 
            
            checkout_data[p_id] = int(qty)
        request.session['checkout_items'] = checkout_data

        return redirect('checkout')
    
    return redirect('cart')

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        
        checkout_data = request.session.get('checkout_items', {})
        products = Products.objects.filter(id__in=checkout_data.keys())
        current_total = Decimal(0)
        for product in products:
            qty = checkout_data[str(product.id)]
            current_total += product.price * qty

        try:

            coupon = Promotions.objects.get(
                code=code,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
            
            if current_total < coupon.min_order_value:
                print('Đơn hàng chưa đạt giá trị tối thiểu để áp dụng mã này.')
            else:

                request.session['coupon_id'] = coupon.id
                request.session['discount_percent'] = float(coupon.discount_percent)
                request.session['coupon_code'] = coupon.code
                print('Mã giảm giá đã được áp dụng.')
        except Promotions.DoesNotExist:
            print('Mã không hợp lệ hoặc hết hạn.')    
    return redirect('checkout')

def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['discount_percent']
        del request.session['coupon_code']
    return redirect('checkout')

def checkout_view(request):
    checkout_data = request.session.get('checkout_items', {})
    
    if not checkout_data:
        return redirect('cart')

    display_items = []
    total_amount = Decimal(0)

    products = Products.objects.filter(id__in=checkout_data.keys())

    for product in products:
        qty = checkout_data[str(product.id)]
        subtotal = product.price * qty
        total_amount += subtotal
        
        display_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })
    now = timezone.now().date()
    valid_coupons = Promotions.objects.filter(start_date__lte=now, end_date__gte=now)    
    discount_percent_float = request.session.get('discount_percent', 0)
    discount_percent = Decimal(str(discount_percent_float)) 
    
    coupon_code = request.session.get('coupon_code', '')
    
    discount_amount = total_amount * (discount_percent / 100)
    final_total = total_amount - discount_amount

    context = {
        'items': display_items,
        'total_amount': total_amount,       
        'discount_percent': discount_percent,
        'discount_amount': discount_amount, 
        'final_total': final_total, 
        'coupon_code': coupon_code,
        'coupons': valid_coupons
    }
    return render(request, 'main/payment.html', context)

def process_checkout(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
            
            checkout_session = request.session.get('checkout_items')
            
            if not checkout_session:
                messages.error(request, "Không có sản phẩm để thanh toán.")
                return redirect('cart')

            items_to_process = []
            total_amount = 0
            
            products = Products.objects.filter(id__in=checkout_session.keys())
            for product in products:
                qty = checkout_session[str(product.id)]
                total = product.price * qty
                items_to_process.append({
                    'product': product,
                    'quantity': qty,
                    'price': product.price
                })
                total_amount += total

            discount_percent_float = request.session.get('discount_percent', 0)
            discount_percent = Decimal(str(discount_percent_float))
            coupon_code = request.session.get('coupon_code', '')

            discount_amount = total_amount * (discount_percent / 100)
            final_amount = total_amount - discount_amount

            promo_obj = None
            if coupon_code:
                try:
                    promo_obj = Promotions.objects.get(code=coupon_code)
                except Promotions.DoesNotExist:
                    pass

            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            
            address_detail = request.POST.get('address')
            ward = request.POST.get('ward')
            province = request.POST.get('province')
            country = request.POST.get('country', 'Vietnam')
            
            note = request.POST.get('note', '')
            payment_method_code = request.POST.get('payment_method', 'cod')

            payment_method, _ = PaymentMethod.objects.get_or_create(name=payment_method_code)

            with transaction.atomic():
                new_order = Orders.objects.create(
                    user=user,
                    payment_method=payment_method,
                    promo=promo_obj,         
                    receiver_name=fullname,
                    receiver_phone=phone,
                    total_amount=total_amount,
                    shipping_fee=0,
                    discount_percent=discount_percent,
                    final_amount=final_amount, 
                    status='Chờ xử lý',
                    note=note,
                    created_at=timezone.now()
                )
                
                OrderAddresses.objects.create(
                    order=new_order,
                    country=country,
                    province=province,
                    ward=ward,
                    address=address_detail
                )

                for item in items_to_process:
                    OrderItems.objects.create(
                        order=new_order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                    product_obj = item['product']
                    product_obj.stock -= item['quantity']
                    product_obj.sold += item['quantity']
                    product_obj.save()

                try:
                    user_cart = Carts.objects.get(user=user)
                    CartItems.objects.filter(
                        cart=user_cart, 
                        product__id__in=checkout_session.keys()
                    ).delete()
                except Carts.DoesNotExist:
                    pass
                
                del request.session['checkout_items']
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
                    del request.session['discount_percent']

            return redirect('account')

        except Exception as e:
            messages.error(request, f"Lỗi thanh toán: {str(e)}")
            print(e)
            return redirect('checkout')

    return redirect('index')
