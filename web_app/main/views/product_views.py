from django.shortcuts import render, redirect
from ..models import Products, Categories

def get_index(request):
    # Lấy top 4 sản phẩm bán chạy
    products = Products.objects.all().order_by('-sold')[:4]
    context = {
        'products': products
    }
    return render(request, 'main/index.html', context)

def get_catalog(request):
    categories = Categories.objects.all()
    products = Products.objects.all()
    
    # Lọc theo danh mục
    active_category = request.GET.get('category')
    if active_category:
        products = products.filter(category_id=active_category)
    
    # Sắp xếp
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
    
    # Sản phẩm liên quan
    related_products = Products.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:4]

    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'main/product.html', context)