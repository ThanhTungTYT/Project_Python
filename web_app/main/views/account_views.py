import re
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
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
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('account')

    message = None
    msg_type = "" 

    if request.method == 'POST':
        try:
            user = Users.objects.get(id=user_id)
            
            old_pass = request.POST.get('old_password', '').strip()
            new_pass = request.POST.get('new_password', '').strip()
            confirm_pass = request.POST.get('confirm_password', '').strip()

            if not old_pass or not new_pass or not confirm_pass:
                message = "Vui lòng nhập đầy đủ thông tin."
                msg_type = "error"
            
            elif not check_password(old_pass, user.password_hash):
                message = "Mật khẩu hiện tại không đúng."
                msg_type = "error"

            elif new_pass != confirm_pass:
                message = "Mật khẩu xác nhận không khớp."
                msg_type = "error"
            
            elif check_password(new_pass, user.password_hash):
                message = "Mật khẩu mới không được trùng với mật khẩu cũ."
                msg_type = "error"
            
            elif (len(new_pass) < 8 or 
                  not re.search(r'[a-z]', new_pass) or 
                  not re.search(r'[A-Z]', new_pass) or 
                  not re.search(r'[0-9]', new_pass) or 
                  not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_pass)):
                message = "Mật khẩu yếu! Cần: 8 ký tự, Hoa, thường, số, ký tự đặc biệt."
                msg_type = "error"
            
            else:
                user.password_hash = make_password(new_pass)
                user.save()
                message = "Đổi mật khẩu thành công!"
                msg_type = "success"

        except Users.DoesNotExist:
            message = "Không tìm thấy người dùng."
            msg_type = "error"

    context = {
        'message': message,
        'msg_type': msg_type
    }
    return render(request, 'main/changepw.html', context)

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