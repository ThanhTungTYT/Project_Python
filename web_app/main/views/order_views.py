from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
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
    code = request.POST.get('coupon_code')
    checkout_data = request.session.get('checkout_items', {})

    products = Products.objects.filter(
        id__in=checkout_data.keys(),
        state='active'
    )

    total = sum(
        p.price * checkout_data[str(p.id)]
        for p in products
    )

    today = timezone.now().date()

    try:
        promo = Promotions.objects.get(
            code=code,
            start_date__lte=today,
            end_date__gte=today,
            state='active',
            quantity__gt=0
        )

        if total < promo.min_order_value:
            messages.warning(request, 'Đơn hàng chưa đủ điều kiện.')
        else:
            request.session['coupon_code'] = promo.code
            messages.success(request, 'Đã áp dụng mã giảm giá.')

    except Promotions.DoesNotExist:
        messages.error(request, 'Mã không hợp lệ.')

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
    valid_coupons = Promotions.objects.filter(start_date__lte=now, end_date__gte=now, state='active', quantity__gt=0)
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
            today = timezone.now().date()
            if coupon_code:
                # Trường hợp khách có nhập mã: chỉ chấp nhận mã đang active và còn lượt
                try:
                    promo_obj = Promotions.objects.get(
                        code=coupon_code,
                        start_date__lte=today,
                        end_date__gte=today,
                        state='active',
                        quantity__gt=0
                    )
                except Promotions.DoesNotExist:
                    promo_obj = None

            if not promo_obj:
                try:
                    promo_obj = Promotions.objects.get(code="NO_PROMO")
                except Promotions.DoesNotExist:
                    promo_obj = Promotions.objects.create(
                        code="NO_PROMO",
                        description="Không áp dụng",
                        discount_percent=0,
                        min_order_value=0,
                        start_date=timezone.now().date(),
                        end_date=timezone.now().date() + timezone.timedelta(days=3650),
                        quantity=999999,
                        state='active'
                    )

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

                # Nếu dùng mã khuyến mãi thực sự (không phải NO_PROMO), cập nhật số lượng còn lại
                try:
                    if promo_obj and promo_obj.code != 'NO_PROMO':
                        try:
                            promo_obj.quantity = max(0, int(promo_obj.quantity) - 1)
                            if promo_obj.quantity == 0:
                                promo_obj.state = 'inactive'
                            promo_obj.save()
                        except Exception:
                            pass
                except Exception:
                    pass

                # Kiểm tra xem khách chọn bank hay cod
                if payment_method.name == 'bank':
                    return redirect('payment_qr', order_id=new_order.id)
                else:
                    messages.success(request, "Đặt hàng thành công!")
                    return redirect('account')
            return redirect('account')
            
        except Exception as e:
            messages.error(request, f"Lỗi thanh toán: {str(e)}")
            print(e)
            return redirect('checkout')

    return redirect('index')

def payment_qr(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    
    MY_BANK = {
        'BANK_ID': 'MB',        
        'ACCOUNT_NO': '0933652267', # SO TAI KHOAN
        'ACCOUNT_NAME': 'NGUYEN HUY BAO', # TEN TAI KHOAN, VIET HOA KHONG DAU
    }
    
    content = f"DH{order.id}"
    
    # LINK NAY TAO RA QR CODE THEO CHUAN VIETQR
    amount = int(order.final_amount) 
    qr_url = f"https://img.vietqr.io/image/{MY_BANK['BANK_ID']}-{MY_BANK['ACCOUNT_NO']}-compact.jpg?amount={amount}&addInfo={content}&accountName={MY_BANK['ACCOUNT_NAME']}"
    
    context = {
        'order': order,
        'qr_url': qr_url,
        'bank_info': MY_BANK,
        'amount': amount
    }
    return render(request, 'main/payment_qr.html', context)

@require_POST
def cancel_order(request, order_id):
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Vui lòng đăng nhập để thực hiện thao tác.")
        return redirect('account') 

    try:
        with transaction.atomic():
            order = Orders.objects.get(id=order_id, user__id=user_id)
            
            if order.status == 'Chờ xử lý':
                order_items = order.orderitems_set.all()
                
                for item in order_items:
                    product = item.product
                    product.stock += item.quantity
                    product.sold -= item.quantity
                    
                    product.save()
                order.status = 'Đã hủy'
                order.save()
                messages.success(request, "Đã hủy đơn hàng thành công.")
            else:
                messages.error(request, "Không thể hủy đơn hàng này.")
            
    except Orders.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng.")
    return redirect('account')

@require_POST
def confirm_order(request, order_id):
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, "Vui lòng đăng nhập để thực hiện thao tác.")
        return redirect('account')

    try:
        order = Orders.objects.get(id=order_id, user__id=user_id)
        
        if order.status == 'Đang giao':
            order.status = 'Đã nhận'
            order.save()
            messages.success(request, "Cảm ơn bạn! Đã xác nhận nhận hàng.")
        else:
            messages.error(request, "Chưa thể xác nhận (Đơn chưa giao hoặc đã hoàn thành).")
            
    except Orders.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng.")

    # 4. Load lại trang account ngay lập tức
    return redirect('account')
