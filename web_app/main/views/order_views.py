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
    code = request.POST.get('coupon_code', '').strip()
    
    # Tính tổng tiền hiện tại để check điều kiện
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
            messages.error(request, f"Đơn hàng chưa đạt giá trị tối thiểu ({coupon.min_order_value:,.0f}đ) để dùng mã này.")
        else:
            request.session['coupon_id'] = coupon.id
            request.session['discount_percent'] = float(coupon.discount_percent)
            request.session['coupon_code'] = coupon.code
            messages.success(request, f"Áp dụng mã {code} thành công! Giảm {coupon.discount_percent}%.")
            
    except Promotions.DoesNotExist:
        messages.error(request, "Mã giảm giá không hợp lệ hoặc đã hết hạn.")
        
    return redirect('checkout')

def remove_coupon(request):
    # Xóa tất cả các key liên quan đến khuyến mãi
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    
    if 'discount_percent' in request.session:
        del request.session['discount_percent']
        
    if 'coupon_id' in request.session:
        del request.session['coupon_id']

    # Thông báo cho người dùng biết đã gỡ
    messages.info(request, "Đã gỡ bỏ mã giảm giá.")
    
    return redirect('checkout')

def checkout_view(request):
    checkout_data = request.session.get('checkout_items', {})
    
    if not checkout_data:
        messages.warning(request, "Không có sản phẩm nào để thanh toán.")
        return redirect('cart')

    display_items = []
    total_amount = Decimal(0)

    # Lấy danh sách sản phẩm từ session
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

    # Tính toán giảm giá
    discount_percent_float = request.session.get('discount_percent', 0)
    discount_percent = Decimal(str(discount_percent_float))
    coupon_code = request.session.get('coupon_code', '')
    
    discount_amount = total_amount * (discount_percent / 100)
    final_total = total_amount - discount_amount

    # Lấy danh sách coupon khả dụng để hiển thị
    now = timezone.now()
    valid_coupons = Promotions.objects.filter(start_date__lte=now, end_date__gte=now)

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
        
        # Bắt buộc đăng nhập (nếu hệ thống yêu cầu)
        if not user_id:
            messages.error(request, "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.")
            return redirect('login')

        try:
            user = Users.objects.get(id=user_id)
            checkout_session = request.session.get('checkout_items')
            
            if not checkout_session:
                messages.error(request, "Không có sản phẩm để thanh toán.")
                return redirect('cart')

            # 1. Tính toán lại tiền và kiểm tra tồn kho
            items_to_process = []
            total_amount = Decimal(0)
            
            products = Products.objects.filter(id__in=checkout_session.keys())
            
            for product in products:
                qty = checkout_session[str(product.id)]
                
                # Kiểm tra tồn kho
                if product.stock < qty:
                    messages.error(request, f"Sản phẩm {product.name} không đủ số lượng tồn kho (Còn: {product.stock}).")
                    return redirect('checkout')

                total = product.price * qty
                items_to_process.append({
                    'product': product,
                    'quantity': qty,
                    'price': product.price
                })
                total_amount += total

            # 2. Tính giảm giá
            discount_percent_float = request.session.get('discount_percent', 0)
            discount_percent = Decimal(str(discount_percent_float))
            coupon_code = request.session.get('coupon_code', '')
            
            discount_amount = total_amount * (discount_percent / 100)
            final_amount = total_amount - discount_amount

            # 3. Lấy hoặc tạo Promo "NO_PROMO" nếu không dùng mã
            promo_obj = None
            
            # Tạo sẵn đối tượng NO_PROMO để fallback (dùng khi không có mã hoặc mã lỗi)
            no_promo, _ = Promotions.objects.get_or_create(
                code="NO_PROMO",
                defaults={
                    'description': 'Không áp dụng',
                    'discount_percent': 0,
                    'min_order_value': 0,
                    'quantity': 999999,  # hoặc 0 nếu bạn muốn
                    'start_date': timezone.now(),
                    'end_date': timezone.datetime(2099, 12, 31, tzinfo=timezone.get_current_timezone()),
                    'state': 'active'
                }
            )

            if coupon_code:
                try:
                    # Dùng select_for_update() để khóa record này lại khi đang xử lý
                    # Giúp tránh lỗi 2 người cùng đặt hàng 1 mã cuối cùng cùng lúc
                    promo_obj = Promotions.objects.select_for_update().get(code=coupon_code)
                    
                    # --- KIỂM TRA VÀ TRỪ SỐ LƯỢNG ---
                    if promo_obj.quantity > 0:
                        promo_obj.quantity -= 1
                        promo_obj.save()
                    else:
                        # Nếu mã hết lượt dùng -> Báo lỗi và hủy transaction (quay về checkout)
                        messages.error(request, "Mã giảm giá đã hết lượt sử dụng.")
                        return redirect('checkout')
                    # --------------------------------

                except Promotions.DoesNotExist:
                    # Nếu session lưu mã bậy hoặc mã bị admin xóa -> Dùng NO_PROMO
                    promo_obj = no_promo
            else:
                # Khách không nhập mã -> Dùng NO_PROMO
                promo_obj = no_promo

            # 4. Lấy thông tin form
            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            address_detail = request.POST.get('address')
            ward = request.POST.get('ward')
            province = request.POST.get('province')
            country = request.POST.get('country', 'Vietnam')
            note = request.POST.get('note', '')
            payment_method_code = request.POST.get('payment_method', 'cod')

            payment_method, _ = PaymentMethod.objects.get_or_create(name=payment_method_code)

            # 5. Transaction: Lưu Orders -> OrderItems -> OrderAddresses -> Trừ kho -> Xóa giỏ hàng
            with transaction.atomic():
                # Tạo đơn hàng
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
                
                # Lưu địa chỉ
                OrderAddresses.objects.create(
                    order=new_order,
                    country=country,
                    province=province,
                    ward=ward,
                    address=address_detail
                )

                # Lưu chi tiết đơn hàng và trừ kho
                for item in items_to_process:
                    OrderItems.objects.create(
                        order=new_order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                    # Trừ kho
                    p = item['product']
                    p.stock -= item['quantity']
                    p.sold += item['quantity']
                    p.save()

                # Xóa các item này trong giỏ hàng (nếu có)
                try:
                    user_cart = Carts.objects.get(user=user)
                    CartItems.objects.filter(
                        cart=user_cart, 
                        product__id__in=checkout_session.keys()
                    ).delete()
                except Carts.DoesNotExist:
                    pass
                
                # 6. Dọn dẹp session
                del request.session['checkout_items']
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']
                    del request.session['discount_percent']
                    del request.session['coupon_id']

                # 7. Điều hướng
                if payment_method.name == 'bank':
                    return redirect('payment_qr', order_id=new_order.id)
                else:
                    messages.success(request, "Đặt hàng thành công!")
                    return redirect('account') # Chuyển về lịch sử đơn hàng
            
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi xử lý đơn hàng: {str(e)}")
            print(f"Error processing checkout: {e}")
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
            # Lấy đơn hàng của user đó
            order = Orders.objects.get(id=order_id, user__id=user_id)
            
            # Chỉ cho phép hủy nếu trạng thái là 'Chờ xử lý'
            if order.status == 'Chờ xử lý':
                # 1. Hoàn trả tồn kho sản phẩm (Logic cũ)
                order_items = order.orderitems_set.all()
                for item in order_items:
                    product = item.product
                    product.stock += item.quantity
                    product.sold -= item.quantity
                    product.save()
                
                # 2. Hoàn trả quantity cho Promotion (Logic MỚI)
                # Kiểm tra xem đơn hàng có dùng mã không và mã đó không phải mã mặc định 'NO_PROMO'
                if order.promo and order.promo.code != 'NO_PROMO':
                    # Giả sử model Promotions có trường 'quantity' là số lượng mã còn lại
                    order.promo.quantity += 1 
                    order.promo.save()

                # 3. Cập nhật trạng thái đơn hàng
                order.status = 'Đã hủy'
                order.save()
                
                messages.success(request, "Đã hủy đơn hàng thành công và hoàn lại mã giảm giá.")
            else:
                messages.error(request, "Không thể hủy đơn hàng này (Đã xử lý hoặc đang giao).")
            
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
