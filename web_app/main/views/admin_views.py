# --- DJANGO CORE IMPORTS ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import HttpResponse 

# --- AUTHENTICATION ---
from django.contrib.auth.hashers import make_password

# --- TIME & DATE HANDLING ---
from django.utils import timezone
from django.utils.dateparse import parse_date
from datetime import timedelta, datetime 

# --- DATABASE & MODELS ---
from django.db.models import Sum, Count, Q 
# Import Models 
from ..models import (
    Products, Categories, ProductImages, Contacts, Users, 
    Orders, Banners, ProductsReview, OrderItems, OrderAddresses, Promotions
)

# --- DATA SCIENCE & VISUALIZATION ---
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# --- UTILITIES (XỬ LÝ ẢNH & ENCODING) ---
import io
import base64
import urllib.parse 


def get_adminPage1(request):
    # 1. XỬ LÝ BỘ LỌC THỜI GIAN
    filter_type = request.GET.get('filter', 'today') 
    
    now = timezone.now()
    today_date = now.date()
    
    # Xác định mốc thời gian bắt đầu
    if filter_type == 'week':
        start_date = now - timedelta(days=7)
        label_filter = "7 ngày qua"
    elif filter_type == 'month':
        start_date = now - timedelta(days=30)
        label_filter = "30 ngày qua"
    elif filter_type == 'quarter':
        start_date = now - timedelta(days=120) # 4 tháng
        label_filter = "1 quý qua"
    else: # today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label_filter = "Hôm nay"

    orders_filtered = Orders.objects.filter(created_at__gte=start_date).exclude(status='Đã hủy')
    users_filtered = Users.objects.filter(created_at__gte=start_date)

    # 2. TÍNH TOÁN KPI
    orders_today = Orders.objects.filter(created_at__date=today_date).exclude(status='Đã hủy')
    revenue_today = orders_today.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    count_orders_filter = orders_filtered.count()
    pending_count = orders_filtered.filter(status='Chờ xử lý').count()
    count_users_filter = users_filtered.count()
    total_revenue_filter = orders_filtered.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # 3. VẼ BIỂU ĐỒ TRÒN (TOP SẢN PHẨM)
    category_stats = OrderItems.objects.filter(
        order__created_at__gte=start_date
    ).exclude(
        order__status='Đã hủy'
    ).values(
        'product__category__name'
    ).annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')

    chart_pie_url = None
    data_category = [{'name': item['product__category__name'], 'count': item['total_qty']} 
                      for item in category_stats if item['total_qty'] > 0]

    if data_category:
        df_pie = pd.DataFrame(data_category)
        fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
        colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']
        
        ax_pie.pie(
            df_pie['count'], labels=df_pie['name'], autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 11}, radius=1.0
        )
        ax_pie.axis('equal')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        buf.seek(0)
        chart_pie_url = urllib.parse.quote(base64.b64encode(buf.read()))
        plt.close(fig_pie)

    # 4. VẼ BIỂU ĐỒ CỘT (DOANH THU)
    chart_bar_url = None
    
    # Lấy dữ liệu từ query chung bên trên (orders_filtered)
    data_revenue = list(orders_filtered.values('created_at', 'total_amount'))
    
    if data_revenue:
        df_bar = pd.DataFrame(data_revenue)
        df_bar['created_at'] = pd.to_datetime(df_bar['created_at'])
        
        # Xử lý gom nhóm dữ liệu theo loại lọc
        if filter_type == 'today':
            df_bar['period'] = df_bar['created_at'].dt.strftime('%H:00')
            xlabel = 'Giờ trong ngày'
        elif filter_type == 'week':
            df_bar['period'] = df_bar['created_at'].dt.strftime('%d/%m')
            xlabel = 'Ngày'
        elif filter_type == 'month':
            df_bar['period'] = df_bar['created_at'].dt.strftime('%d/%m')
            xlabel = 'Ngày trong tháng'
        else: # quarter
            df_bar['period'] = df_bar['created_at'].dt.strftime('T%m')
            xlabel = 'Tháng'

        # Tính tổng tiền theo period (nhóm lại)
        df_bar_grouped = df_bar.groupby('period')['total_amount'].sum().reset_index()

        # Vẽ biểu đồ
        fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
        
        # Vẽ cột
        ax_bar.bar(df_bar_grouped['period'], df_bar_grouped['total_amount'], color='#A0522D', width=0.5)
        
        # Trang trí
        ax_bar.set_ylabel('Doanh thu (VND)')
        ax_bar.set_xlabel(xlabel)
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Format số tiền (vd: 1,000,000)
        ax_bar.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        plt.xticks(rotation=0)
        plt.tight_layout()

        buf_bar = io.BytesIO()
        plt.savefig(buf_bar, format='png', transparent=True)
        buf_bar.seek(0)
        chart_bar_url = urllib.parse.quote(base64.b64encode(buf_bar.read()))
        plt.close(fig_bar)

    context = {
        'revenue_today': revenue_today,
        'count_orders_filter': count_orders_filter,
        'pending_count': pending_count,
        'count_users_filter': count_users_filter,
        'total_revenue_filter': total_revenue_filter,
        'label_filter': label_filter,
        'current_filter': filter_type,
        'chart_pie_url': chart_pie_url,
        'chart_bar_url': chart_bar_url,
    }
    
    return render(request, 'main/adminPage1.html', context)

def get_adminPage2(request):
    # Lấy danh sách danh mục để đổ vào thẻ <select>
    categories = Categories.objects.all()

    # 1. Query gốc: Lấy tất cả sản phẩm, sắp xếp mới nhất lên đầu
    products_list = Products.objects.select_related('category').prefetch_related('productimages_set').all().order_by('-id')

    # 2. Xử lý Tìm kiếm (Search)
    search_query = request.GET.get('q', '')
    if search_query:
        products_list = products_list.filter(name__icontains=search_query)

    # 3. Xử lý Bộ lọc (Filter)
    category_filter = request.GET.get('category_filter', '')
    if category_filter and category_filter != 'all':
        products_list = products_list.filter(category_id=category_filter)

    # 4. PHÂN TRANG (Paginator) - Code giống mẫu bạn yêu cầu
    paginator = Paginator(products_list, 25) # Mỗi trang 25 sản phẩm
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. Truyền context
    context = {
        'products': page_obj,  # Quan trọng: Truyền page_obj thay vì products_list
        'categories': categories,
        'search_query': search_query, # Để giữ lại chữ trong ô tìm kiếm
        # Chuyển category_filter về int để so sánh trong template (nếu có)
        'category_filter': int(category_filter) if category_filter.isdigit() else 'all'
    }
    
    return render(request, 'main/adminPage2.html', context)

def add_product(request):
    if request.method == 'POST':
        try:
            ten_sp = request.POST.get('name')
            loai_sp_id = request.POST.get('category')
            trang_thai = request.POST.get('state')
            gia_sp = request.POST.get('price')
            khoi_luong = request.POST.get('weight')
            so_luong = request.POST.get('quantity')
            mo_ta = request.POST.get('description')
            list_anh = request.POST.get('image_url', '')

            cat = Categories.objects.get(id=loai_sp_id)
            
            new_product = Products.objects.create(
                name=ten_sp,
                category=cat,
                state=trang_thai,
                price=gia_sp,
                weight_grams=khoi_luong,
                stock=so_luong,
                description=mo_ta,
                sold=0,
                created_at=timezone.now()
            )
            # cắt chuổi bằng xuống dòng hoặc dấu phẩy để lấy url ảnh
            urls = list_anh.replace('\n', ',').split(',')
            for url in urls:
                url_clean = url.strip()
                if url_clean:
                    ProductImages.objects.create(product=new_product, image_url=url_clean)
            

        except Categories.DoesNotExist:
            messages.error(request, "Lỗi: Loại sản phẩm không hợp lệ.")
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")

    return redirect('adminPage2')

def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, id=product_id)
            
            has_sold = OrderItems.objects.filter(product=product).exists()
            
            if has_sold:
                product.state = 'inactive' 
                product.stock = 0
                product.save()
            else:
                product_name = product.name 
                
                product.productimages_set.all().delete()
                
                product.delete()
                
            
        except Exception as e:
            print(e)

    return redirect('adminPage2')


def edit_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, id=product_id)
            
            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            product.state = request.POST.get('state')
            
            product.weight_grams = int(request.POST.get('weight')) 
            product.stock = int(request.POST.get('quantity'))
            
            product.description = request.POST.get('description')
            
            cat_id = request.POST.get('category')
            if cat_id:
                product.category = get_object_or_404(Categories, id=cat_id)

            product.save()
            
        except Exception as e:
            print("Lỗi Update:", e) 
    
    return redirect('adminPage2')

def get_adminPage3(request):
    if request.method == "POST" and 'btn_export_invoice' in request.POST:
        order_id_to_update = request.POST.get('order_id_hidden')
        order_update = Orders.objects.get(id=order_id_to_update)
            
        if order_update.status in ['Chờ xử lý']: 
            order_update.status = 'Đang giao'
            order_update.save()
        
        page_current = request.GET.get('page', 1)
        return redirect(f'/adminPage3/?page={page_current}')

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
    banners_list = Banners.objects.all().order_by('-id')
    context = {'banners_list': banners_list}
    return render(request, 'main/adminPage7.html', context)

def add_banner(request):
    if request.method == 'POST':
        try:
            Banners.objects.create(
                banner_url=request.POST.get('banner_image_url'),
                status=request.POST.get('status'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
            )
        except Exception as e:
            print(f"Lỗi thêm: {e}")
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
            print(f"Lỗi sửa: {e}")
    return redirect('adminPage7')

def delete_banner(request, banner_id):
    if request.method == 'POST':
        try:
            banner = get_object_or_404(Banners, id=banner_id)
            banner.delete()
        except Exception as e:
            print(f"Lỗi xóa: {e}")
    return redirect('adminPage7')

def get_adminPage8(request):
    query = request.GET.get('q', '')
    
    if query:
        promotions = Promotions.objects.filter(
            Q(code__icontains=query) | Q(description__icontains=query)
        ).order_by('-id')
    else:
        promotions = Promotions.objects.all().order_by('-id')
    
    context = {
        'promotions': promotions,
        'query': query  
    }
    return render(request, 'main/adminPage8.html', context)

def add_discount(request):
    if request.method == 'POST':
        try:
            code = request.POST.get('code')
            
            if Promotions.objects.filter(code=code).exists():
                messages.error(request, 'Mã giảm giá này đã tồn tại!')
                return redirect('adminPage8')

            description = request.POST.get('description')
            min_order_value = request.POST.get('min_order_value')
            discount_percent = request.POST.get('discount_percent')
            quantity = request.POST.get('quantity')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            state = request.POST.get('state')

            Promotions.objects.create(
                code=code,
                description=description,
                min_order_value=float(min_order_value),
                discount_percent=float(discount_percent),
                quantity=int(quantity),
                start_date=start_date,
                end_date=end_date,
                state=state
            )
            messages.success(request, 'Thêm mã giảm giá thành công!')
            
        except Exception as e:
            print(f"Lỗi thêm mã: {e}")
            messages.error(request, 'Có lỗi xảy ra khi thêm mã.')

    return redirect('adminPage8')

def update_discount(request, promo_id):
    if request.method == 'POST':
        try:
            promo = get_object_or_404(Promotions, id=promo_id)
            
            
            promo.description = request.POST.get('description')
            promo.min_order_value = float(request.POST.get('min_order_value'))
            promo.discount_percent = float(request.POST.get('discount_percent'))
            promo.quantity = int(request.POST.get('quantity'))
            promo.start_date = request.POST.get('start_date')
            promo.end_date = request.POST.get('end_date')
            promo.state = request.POST.get('state')
            
            promo.save()
            messages.success(request, f'Cập nhật mã {promo.code} thành công!')
            
        except Exception as e:
            print(f"Lỗi sửa mã: {e}")
            messages.error(request, 'Lỗi cập nhật mã giảm giá.')

    return redirect('adminPage8')

def delete_discount(request, promo_id):
    if request.method == 'POST':
        try:
            promo = get_object_or_404(Promotions, id=promo_id)

            has_used = Orders.objects.filter(promo=promo).exists()

            if has_used:
                promo.state = 'inactive'
                promo.quantity = 0
                promo.save()
                messages.warning(request, 'Mã đã được sử dụng nên chỉ chuyển sang trạng thái Inactive.')
            else:
                promo.delete()
                messages.success(request, 'Đã xóa mã giảm giá.')

        except Exception as e:
            print(e)
            messages.error(request, 'Lỗi khi xóa mã.')

    return redirect('adminPage8')