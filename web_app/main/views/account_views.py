from django.shortcuts import render, redirect
from ..models import Users

def get_account(request):
    # Trang khung Account
    return render(request, 'main/account.html')

def get_info(request):
    user_id = request.session.get('user_id')
    
    try:
        current_user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        # Nếu session lỗi hoặc user bị xóa, trả về info rỗng hoặc redirect
        return render(request, 'main/info.html')
        
    context = {
        'user': current_user 
    }
    return render(request, 'main/info.html', context)

def get_changepw(request):
    return render(request, 'main/changepw.html')

def get_history(request):
    return render(request, 'main/history.html')