# views/order_views.py
from django.utils import timezone
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
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

def checkout_view(request):
    checkout_data = request.session.get('checkout_items', {})
    
    if not checkout_data:
        return redirect('cart')

    display_items = []
    total_amount = 0

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

    context = {
        'items': display_items,
        'total_amount': total_amount
    }
    return render(request, 'main/payment.html', context)

def process_checkout(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
            
            checkout_session = request.session.get('checkout_items')
            items_to_process = []
            total_amount = 0

            if checkout_session:
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
            else:
                cart = Carts.objects.get(user=user)
                cart_items = CartItems.objects.filter(cart=cart)
                
                if not cart_items.exists():
                    messages.error(request, "Giỏ hàng trống!")
                    return redirect('cart')

                for item in cart_items:
                    total = item.product.price * item.quantity
                    items_to_process.append({
                        'product': item.product,
                        'quantity': item.quantity,
                        'price': item.product.price
                    })
                    total_amount += total

            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')

            address_detail = request.POST.get('address')
            ward = request.POST.get('ward')
            province = request.POST.get('province')
            country = request.POST.get('country', 'Vietnam')
            
            note = request.POST.get('note', '')
            payment_method_code = request.POST.get('payment_method', 'cod')

            payment_method, _ = PaymentMethod.objects.get_or_create(
                name=payment_method_code
            )

            try:
                promo = Promotions.objects.get(id=1)
            except:
                promo = Promotions.objects.create(
                    code="NO_PROMO", 
                    description="Không áp dụng",
                    discount_percent=0,
                    min_order_value=0,
                    start_date=timezone.now(), 
                    end_date=timezone.now()
                )
            with transaction.atomic():
                new_order = Orders.objects.create(
                    user=user,
                    payment_method=payment_method,
                    promo=promo,
                    receiver_name=fullname,
                    receiver_phone=phone,
                    total_amount=total_amount,
                    shipping_fee=0,      
                    discount_percent=0,
                    final_amount=total_amount, 
                    status='Đang xử lý',    
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
                    if checkout_session:
                        CartItems.objects.filter(
                            cart=user_cart, 
                            product__id__in=checkout_session.keys()
                        ).delete()
                        del request.session['checkout_items']
                    else:
                        CartItems.objects.filter(cart=user_cart).delete()
                except Carts.DoesNotExist:
                    pass
            return redirect('account')

        except Exception as e:
            messages.error(request, f"Lỗi thanh toán: {str(e)}")
            return redirect('checkout')

    return redirect('index')
