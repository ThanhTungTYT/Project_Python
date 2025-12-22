from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

# Import chuẩn xác từ app main
from ..models import Products, Categories, ProductImages

# --- Trang Admin 1 (Tổng quan) ---
def get_adminPage1(request):
    return render(request, 'main/adminPage1.html')

# --- Trang Admin 2 (Quản lý sản phẩm & Thêm mới) ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..models import Products, Categories, ProductImages

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
def get_adminPage5(request): return render(request, 'main/adminPage5.html')
def get_adminPage6(request): return render(request, 'main/adminPage6.html')
def get_adminPage7(request): return render(request, 'main/adminPage7.html')
def get_adminPage8(request): return render(request, 'main/adminPage8.html')