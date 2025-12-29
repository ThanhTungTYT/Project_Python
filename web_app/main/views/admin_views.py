from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.utils.dateparse import parse_date
from django.db.models import Q
from ..models import Products, Categories, ProductImages, Contacts, Users, Orders, Banners, ProductsReview, OrderItems, OrderAddresses, Promotions


def get_adminPage1(request):
    orders_now = Orders.objects.all().filter(created_at=timezone.now())
    users_now = Users.objects.all().filter(created_at=timezone.now())
    orders_month = Orders.objects.all().filter(created_at__month=timezone.now().month)
    orders_near = Orders.objects.all().filter(created_at__gte=timezone.now()-timezone.timedelta(days=7))
    categories = Categories.objects.all()
    count_category = []
    for category in categories:
        products = orders_month.filter(orderitems__product__category=category).distinct()
        count_category.append((category.name, products.count()))
    count_users = users_now.count()
    sum_date = 0
    orders_count = orders_now.count()
    for order in orders_now:
        sum_date += order.total_amount
    sum_month = 0
    for order in orders_month:
        sum_month += order.total_amount
    avg_month = sum_month / orders_month.count() if orders_month.count() > 0 else 0
    context = {
        'orders_now': orders_now,
        'orders_month': orders_month,
        'orders_count': orders_count,
        'sum_date': sum_date,
        'sum_month': sum_month,
        'users_now': users_now,
        'count_users': count_users,
        'avg_month': avg_month,
        'orders_near': orders_near,
        'count_category': count_category,
    }
    return render(request, 'main/adminPage1.html', context)

def get_adminPage2(request):
    if request.method == 'POST':
        ten_sp = request.POST.get('name')
        loai_sp_id = request.POST.get('category')
        gia_sp = request.POST.get('price')
        khoi_luong = request.POST.get('weight')
        so_luong = request.POST.get('quantity')
        mo_ta = request.POST.get('description')
        list_anh = request.POST.get('image_url', '')

        try:
            cat = Categories.objects.get(id=loai_sp_id)
            
            new_product = Products.objects.create(
                name=ten_sp,
                category=cat,
                price=gia_sp,
                weight_grams=khoi_luong,
                stock=so_luong,
                description=mo_ta,
                sold=0,
                created_at=timezone.now()
            )
            urls = list_anh.replace('\n', ',').split(',')
            for url in urls:
                url_clean = url.strip()
                if url_clean:
                    ProductImages.objects.create(product=new_product, image_url=url_clean)
        except (Categories.DoesNotExist, Exception) as e:
            print(e)

    products = Products.objects.select_related('category').all().order_by('id')
    return render(request, 'main/adminPage2.html', {'products': products})



def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, id=product_id)
            
            product_name = product.name 
            
            product.productimages_set.all().delete()
            
            product.delete()
            
        except Exception as e:
            print(e);
    return redirect('adminPage2')

def edit_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, id=product_id)
            
            product.name = request.POST.get('name')
            
            product.price = request.POST.get('price')
            product.weight_grams = request.POST.get('weight')
            product.stock = request.POST.get('quantity')
            product.description = request.POST.get('description')
            
            cat_id = request.POST.get('category')
            if cat_id:
                product.category = get_object_or_404(Categories, id=cat_id)

            product.save()            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {e}')
    
    return redirect('adminPage2')

def get_adminPage3(request):
    # 1. XỬ LÝ POST (Cập nhật trạng thái) - Đưa lên đầu để xử lý xong mới load lại dữ liệu
    if request.method == "POST" and 'btn_export_invoice' in request.POST:
        order_id_to_update = request.POST.get('order_id_hidden')
            # Lấy đơn hàng
        order_update = Orders.objects.get(id=order_id_to_update)
            
            # KIỂM TRA
        if order_update.status in ['Chờ xử lý']: 
            order_update.status = 'Đang giao'
            order_update.save()

                      
        # Redirect lại trang hiện tại để làm mới dữ liệu và tránh resubmit form
        page_current = request.GET.get('page', 1)
        return redirect(f'/adminPage3/?page={page_current}')

    # 2. QUERY DỮ LIỆU (Phần hiển thị)
    orders_list = Orders.objects.select_related('user').prefetch_related(
        'orderitems_set__product', 
        'orderaddresses_set'
    ).all().order_by('-created_at')

    # 3. Xử lý LỌC & TÌM KIẾM
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('q')

    if start_date and end_date:
        orders_list = orders_list.filter(created_at__range=[start_date, end_date])
    
    if search_query:
        orders_list = orders_list.filter(
            Q(user__full_name__icontains=search_query) | 
            Q(id__icontains=search_query) |
            Q(receiver_name__icontains=search_query) # Thêm tìm theo tên người nhận
        )

    # 4. PHÂN TRANG
    paginator = Paginator(orders_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'start_date': start_date if start_date else '',
        'end_date': end_date if end_date else '',
        'search_query': search_query if search_query else '',
    }
    return render(request, 'main/adminPage3.html', context)

    
    
def get_adminPage4(request): 
    accounts = Users.objects.all().order_by('id')
    accounts_now = Users.objects.filter(created_at__date=timezone.now().date()).order_by('id')
    context = {
        'accounts': accounts,
        'accounts_now': accounts_now
    }
    return render(request, 'main/adminPage4.html', context)

def delete_account(request, user_id):
    if request.method == 'POST':
        try:
            user = Users.objects.get(id=user_id)
            user.delete()
        except Exception:
            pass
    return redirect('adminPage4')

def add_account(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            role = request.POST.get('role')

            Users.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=make_password(password),
                role=role,
                created_at=timezone.now()
            )
        except Exception as e:
            pass
        
    return redirect('adminPage4')

def get_adminPage5(request):
    if request.method == 'POST':
        
        recipient_email = request.POST.get('recipient_email')
        reply_subject = request.POST.get('reply_subject')
        reply_message = request.POST.get('reply_message')
            
        send_mail(
            subject=f"[Aroma Café Support] {reply_subject}", 
            message=reply_message,                          
            from_email=settings.EMAIL_HOST_USER,             
            recipient_list=[recipient_email],                
            fail_silently=False,
        )
        
        return redirect('adminPage5')

    contacts_list = Contacts.objects.all().order_by('-sent_at')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if start_date and end_date:
            contacts_list = contacts_list.filter(sent_at__date__range=[start_date, end_date])
    
    paginator = Paginator(contacts_list, 25) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'start_date': start_date_str, 
        'end_date': end_date_str,
    }
    
    return render(request, 'main/adminPage5.html', context)

def get_adminPage6(request):

    reviews_list = ProductsReview.objects.select_related('product', 'user').all().order_by('-created_at')


    search_query = request.GET.get('q', '')
    if search_query:
        reviews_list = reviews_list.filter(
            Q(user__full_name__icontains=search_query) | 
            Q(product__name__icontains=search_query)
        )


    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if start_date and end_date:
                reviews_list = reviews_list.filter(created_at__date__range=[start_date, end_date])
        except Exception as e:
            print(f"Lỗi parse date: {e}")

    context = {
        'reviews': reviews_list,
        'search_query': search_query,
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    return render(request, 'main/adminPage6.html', context)

def delete_review(request, review_id):
    if request.method == 'POST':
        try:
            review = get_object_or_404(ProductsReview, id=review_id)
            review.delete()
            messages.success(request, "Đã xóa đánh giá thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi xóa: {e}")
    return redirect('adminPage6')

def get_adminPage7(request):
    banners_list = Banners.objects.all().order_by('id')
    context = {
        'banners_list': banners_list,
    } 
    return render(request, 'main/adminPage7.html', context)

def add_banner(request):
    if request.method == 'POST':
        try:
            banner_image_url = request.POST.get('banner_image_url')
            banner_status = request.POST.get('status')
            banner_start_date = request.POST.get('start_date')
            banner_end_date = request.POST.get('end_date')
            Banners.objects.create(
                banner_url=banner_image_url,
                status=banner_status,
                start_date=banner_start_date,   
                end_date=banner_end_date,
            )
        except Exception as e:
            print(e)
        
    return redirect('adminPage7')

def update_banner(request, banner_id):
    if request.method == 'POST':
        try:
            banner = get_object_or_404(Banners, id=banner_id)

            banner.banner_url = request.POST.get('banner_image_url')
            banner.status = request.POST.get('status')
            banner.start_date = request.POST.get('start_date')
            banner.end_date = request.POST.get('end_date')
            banner.save()
        except Exception as e:
            print(e)
        
    return redirect('adminPage7')

def get_adminPage8(request):
    promotions = Promotions.objects.all().order_by('-id')
    return render(request, 'main/adminPage8.html', {'promotions': promotions})

# 2. Thêm mã mới
def add_discount(request):
    if request.method == 'POST':
        try:
            code = request.POST.get('code')
            if Promotions.objects.filter(code=code).exists():
                messages.error(request, 'Mã này đã tồn tại!')
                return redirect('adminPage8')

            Promotions.objects.create(
                code=code,
                description=request.POST.get('description'),
                min_order_value=request.POST.get('min_order_value'),
                discount_percent=request.POST.get('discount_percent'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date')
            )
            
        except Exception as e:
            print(e)
            
    return redirect('adminPage8')

# 3. Xóa mã
def delete_discount(request, promo_id):
    try:
        Promotions.objects.get(id=promo_id).delete()
    except:
        pass
    return redirect('adminPage8')