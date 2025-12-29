# views/order_views.py
from django.views.decorators.http import require_POST
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

            # --- TÍNH TOÁN LẠI TỔNG TIỀN ---
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

            # --- TÍNH GIẢM GIÁ ---
            discount_percent_float = request.session.get('discount_percent', 0)
            discount_percent = Decimal(str(discount_percent_float))
            coupon_code = request.session.get('coupon_code', '')

            discount_amount = total_amount * (discount_percent / 100)
            final_amount = total_amount - discount_amount

            # Lấy đối tượng Promo nếu có mã
            if coupon_code:
                # Trường hợp khách có nhập mã
                try:
                    promo_obj = Promotions.objects.get(code=coupon_code)
                except Promotions.DoesNotExist:
                    promo_obj = Promotions.objects.get(code="NO_PROMO")
            else:
                try:
                    promo_obj = Promotions.objects.get(code="NO_PROMO")
                except Promotions.DoesNotExist:
                    promo_obj = Promotions.objects.create(
                        code="NO_PROMO",
                        description="Không áp dụng",
                        discount_percent=0,
                        min_order_value=0,
                        start_date=timezone.now(),
                        end_date=timezone.now() + timezone.timedelta(days=3650)
                    )

            # Lấy thông tin giao hàng
            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            
            address_detail = request.POST.get('address')
            ward = request.POST.get('ward')
            province = request.POST.get('province')
            country = request.POST.get('country', 'Vietnam')
            
            note = request.POST.get('note', '')
            payment_method_code = request.POST.get('payment_method', 'cod')

            payment_method, _ = PaymentMethod.objects.get_or_create(name=payment_method_code)

            # --- TẠO ĐƠN HÀNG 
            with transaction.atomic():
                new_order = Orders.objects.create(
                    user=user,
                    payment_method=payment_method,
                    promo=promo_obj,           # Lưu mã khuyến mãi đã dùng
                    receiver_name=fullname,
                    receiver_phone=phone,
                    total_amount=total_amount, # Giá gốc
                    shipping_fee=0,
                    discount_percent=discount_percent, # Lưu % giảm
                    final_amount=final_amount, # Giá cuối cùng khách phải trả
                    status='Chờ xử lý',
                    note=note,
                    created_at=timezone.now()
                )
                
                # Lưu địa chỉ
                OrderAddresses.objects.create(
                    order=new_order,
                    country=country,
                    province=province,
                    ward=ward,
                    address=address_detail
                )

                # Lưu chi tiết sản phẩm & Trừ kho
                for item in items_to_process:
                    OrderItems.objects.create(
                        order=new_order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                    # Trừ tồn kho
                    product_obj = item['product']
                    product_obj.stock -= item['quantity']
                    product_obj.sold += item['quantity']
                    product_obj.save()

                # Xóa sản phẩm khỏi giỏ hàng
                try:
                    user_cart = Carts.objects.get(user=user)
                    CartItems.objects.filter(
                        cart=user_cart, 
                        product__id__in=checkout_session.keys()
                    ).delete()
                except Carts.DoesNotExist:
                    pass
                
                # --- DỌN DẸP SESSION ---
                request.session.pop('checkout_items', None) # Xóa an toàn, không có thì thôi, không báo lỗi
                
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
                    del request.session['discount_percent']

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
    
    # 1. Kiểm tra đăng nhập
    if not user_id:
        messages.error(request, "Vui lòng đăng nhập để thực hiện thao tác.")
        return redirect('account') # Load lại trang account

    try:
        # 2. Tìm đơn hàng
        order = Orders.objects.get(id=order_id, user__id=user_id)
        
        # 3. Xử lý logic
        if order.status == 'Chờ xử lý':
            order.status = 'Đã hủy'
            order.save()
            messages.success(request, "Đã hủy đơn hàng thành công.")
        else:
            messages.error(request, "Không thể hủy đơn hàng này (Trạng thái không hợp lệ).")
            
    except Orders.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn hàng.")

    # 4. QUAN TRỌNG: Load lại trang account ngay lập tức
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
