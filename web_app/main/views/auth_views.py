from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from ..models import Users, Carts

def get_login(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            user = Users.objects.get(email=email_input)

            if check_password(password_input, user.password_hash):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.full_name
                request.session.set_expiry(3600)

                if user.role == 'admin':
                    return redirect('adminPage1')
                return redirect('index')
            else:
                messages.error(request, "Sai mật khẩu!")

        except Users.DoesNotExist:
            messages.error(request, "Email chưa được đăng ký!")
            
    return render(request, 'main/login.html')

def get_register(request):
    if request.method == 'POST':
        yourname = request.POST.get('yourname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')

        if password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp!")
            return render(request, 'main/register.html')

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được sử dụng!")
            return render(request, 'main/register.html')

        try:
            new_user = Users(
                full_name=yourname,
                email=email,
                phone=phone,
                password_hash=make_password(password),
                role='customer'
            )
            new_user.save()

            Carts.objects.create(user=new_user, created_at=timezone.now())

            return redirect('login')

        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {e}")
            return render(request, 'main/register.html')
            
    return render(request, 'main/register.html')

def get_logout(request):
    request.session.flush()
    return redirect('index')

def get_forgotpassword(request):
    return render(request, 'main/forgotpassword.html')