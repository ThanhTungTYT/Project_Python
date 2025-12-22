from django.shortcuts import render, redirect
from ..models import Orders, Users

def get_account(request):
    return render(request, 'main/account.html')

def get_info(request):
    user_id = request.session.get('user_id')
    
    try:
        current_user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return render(request, 'main/info.html')
        
    context = {
        'user': current_user 
    }
    return render(request, 'main/info.html', context)

def get_changepw(request):
    return render(request, 'main/changepw.html')

def get_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = Users.objects.get(id=user_id)
        orders = Orders.objects.filter(user=user).order_by('-created_at').prefetch_related('orderitems_set', 'orderitems_set__product')
        
        context = {
            'orders': orders
        }
        return render(request, 'main/history.html', context)
    except Users.DoesNotExist:
        return redirect('login')