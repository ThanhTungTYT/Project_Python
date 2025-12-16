from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from ..models import Products, Categories, ProductsReview, Users

def get_index(request):
    try:
        products = Products.objects.all().order_by('-sold')[:4]
    except:
        products = []
    return render(request, 'main/index.html', {'products': products})

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

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Bạn cần đăng nhập để viết đánh giá!")
            return redirect(f'/product/{product_id}/')

        try:
            rating_val = request.POST.get('rating')
            comment_val = request.POST.get('comment')
            
            if not rating_val:
                messages.error(request, "Vui lòng chọn số sao đánh giá!")
            else:
                user_instance = Users.objects.get(id=user_id)
                
                ProductsReview.objects.create(
                    product=product,
                    user=user_instance,
                    rating=int(rating_val),
                    comment=comment_val,
                    created_at=timezone.now()
                )
                messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
                
                return redirect(f'/product/{product_id}/')

        except Exception as e:
            messages.error(request, f"Lỗi khi gửi đánh giá: {e}")

    reviews = ProductsReview.objects.filter(product=product).order_by('-created_at')
    
    avg_rating = 0
    if reviews.count() > 0:
        total_score = sum(r.rating for r in reviews)
        avg_rating = round(total_score / reviews.count(), 1)

    related_products = Products.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'related_products': related_products
    }
    return render(request, 'main/product.html', context)