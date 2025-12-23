from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.dateparse import parse_date

# Import chuẩn xác từ app main
from ..models import Products, Categories, ProductImages, Contacts

# --- Trang Admin 1 (Tổng quan) ---
def get_adminPage1(request):
    return render(request, 'main/adminPage1.html')

# --- Trang Admin 2 (Quản lý sản phẩm & Thêm mới) ---
def get_adminPage2(request):
    if request.method == 'POST':
        # Lấy dữ liệu
        ten_sp = request.POST.get('name')
        loai_sp_id = request.POST.get('category')
        gia_sp = request.POST.get('price')
        khoi_luong = request.POST.get('weight')
        so_luong = request.POST.get('quantity')
        mo_ta = request.POST.get('description')
        # Lấy chuỗi ảnh (nhiều link phân cách bởi dấu phẩy hoặc xuống dòng)
        list_anh = request.POST.get('image_url', '')

        try:
            cat = Categories.objects.get(id=loai_sp_id)
            
            # 1. Tạo sản phẩm
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

            # 2. Xử lý lưu nhiều ảnh
            # Tách chuỗi bằng dấu phẩy (,) hoặc xuống dòng (\n)
            urls = list_anh.replace('\n', ',').split(',')
            for url in urls:
                url_clean = url.strip()
                if url_clean:
                    ProductImages.objects.create(product=new_product, image_url=url_clean)

            messages.success(request, 'Đã thêm sản phẩm thành công!')
            return redirect('adminPage2')

        except Categories.DoesNotExist:
            messages.error(request, 'Lỗi: Loại sản phẩm không tồn tại.')
        except Exception as e:
            messages.error(request, f'Lỗi hệ thống: {e}')

    products = Products.objects.select_related('category').all().order_by('-id')
    return render(request, 'main/adminPage2.html', {'products': products})

# --- View mới: Xử lý SỬA sản phẩm ---
def update_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, id=product_id)
            
            # Cập nhật thông tin cơ bản
            product.name = request.POST.get('name')
            product.category_id = request.POST.get('category')
            product.price = request.POST.get('price')
            product.weight_grams = request.POST.get('weight')
            product.stock = request.POST.get('quantity')
            product.description = request.POST.get('description')
            product.save()

            # Cập nhật ảnh (Xóa cũ -> Thêm mới để đơn giản hóa logic)
            list_anh = request.POST.get('image_url', '')
            if list_anh:
                # Chỉ xóa và thêm lại nếu người dùng có nhập ảnh mới
                ProductImages.objects.filter(product=product).delete()
                urls = list_anh.replace('\n', ',').split(',')
                for url in urls:
                    url_clean = url.strip()
                    if url_clean:
                        ProductImages.objects.create(product=product, image_url=url_clean)

            messages.success(request, f'Đã cập nhật sản phẩm {product.name}!')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {e}')
            
    return redirect('adminPage2')

# --- Các View khác giữ nguyên ---
def get_adminPage3(request): return render(request, 'main/adminPage3.html')
def get_adminPage4(request): return render(request, 'main/adminPage4.html')

def get_adminPage5(request):
    if request.method == 'POST':
        try:
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
            messages.success(request, f"Đã gửi phản hồi thành công đến {recipient_email}!")
        except Exception as e:
            messages.error(request, f"Lỗi khi gửi mail: {e}")
        
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

def get_adminPage6(request): return render(request, 'main/adminPage6.html')
def get_adminPage7(request): return render(request, 'main/adminPage7.html')
def get_adminPage8(request): return render(request, 'main/adminPage8.html')