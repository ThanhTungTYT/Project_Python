from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Q, Sum
from ..models import Banners, Products, Categories, ProductsReview, Users, ProductImages
from ai_model import filter_engine

def get_index(request):
    context = {
        'products': [],
        'banners': []
    }
    try:
        products = Products.objects.filter(
            state='active', 
            orderitems__order__created_at__year=timezone.now().year,
            orderitems__order__created_at__month=timezone.now().month,
            orderitems__order__status='Đã nhận' 
        ).annotate(
            sold_in_month=Sum('orderitems__quantity')
        ).order_by(
            '-sold_in_month'
        )[:4]
        
        banners = Banners.objects.filter(status='active')
        context['products'] = products
        context['banners'] = banners
        return render(request, 'main/index.html', context)
    except Exception as e:
        print(f"Lỗi truy vấn trang chủ: {e}")
    return render(request, 'main/index.html', context)

def get_catalog(request):
    categories = Categories.objects.all()
    products = Products.objects.filter(state='active')
    
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

def get_search(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Products.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            state='active'
        )
    
    context = {
        'query': query,
        'products': products,
        'count': products.count() if query else 0
    }
    return render(request, 'main/search.html', context)

def get_product(request, product_id):
    try:
        product = Products.objects.get(state='active', id=product_id)
        imagelist = ProductImages.objects.filter(product=product)
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

            is_toxic, reason = filter_engine.is_toxic(comment_val)
            if is_toxic:
                messages.error(request, f"Bình luận không hợp lệ: {reason}")
                return redirect(f'/product/{product_id}/')
            
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "Bạn cần đăng nhập để viết đánh giá!")
                return redirect(f'/product/{product_id}/')
            
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

    related_products = Products.objects.filter(state='active', category=product.category).exclude(id=product.id).order_by('?')[:4]

    context = {
        'product': product,
        'imagelist': imagelist,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'related_products': related_products
    }
    return render(request, 'main/product.html', context)