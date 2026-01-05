import string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.mail import send_mail 
from django.conf import settings
from ..models import Users, Carts
import re, random, time

def get_login(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')

        try:
            user = Users.objects.get(email=email_input)

            if check_password(password_input, user.password_hash):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.full_name
                request.session['role'] = user.role
                request.session.set_expiry(3600)

                if user.role == 'admin':
                    return redirect('adminPage1')
                return redirect('index')
            else:
                messages.error(request, "Sai mật khẩu!")

        except Users.DoesNotExist:
            messages.error(request, "Email chưa được đăng ký!")
            
    return render(request, 'main/login.html')

def send_otp_email(email):
    otp = str(random.randint(100000, 999999))
    subject = 'Mã xác thực Aroma Café'
    message = f'Mã OTP của bạn là: {otp}. Mã có hiệu lực trong 10 phút.'
    
    try:
        send_mail(
            subject, 
            message, 
            settings.EMAIL_HOST_USER, 
            [email], 
            fail_silently=False
        )
        return otp 
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")
        return None 


def get_register(request):
    if request.method == 'POST':
        name = request.POST.get('yourname')
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
            
        if len(password) < 8 or not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, "Mật khẩu yếu! Cần: 8 ký tự, Hoa, thường, số, ký tự đặc biệt.")
            return render(request, 'main/register.html')

        otp_code = send_otp_email(email)

        if otp_code:
            request.session['reg_temp'] = {
                'full_name': name,
                'email': email,
                'phone': phone,
                'password': make_password(password),
                'otp': otp_code,
                'exp_time': time.time() + 600,   
                'next_resend': time.time() + 120 
            }
            messages.success(request, f"Đã gửi mã OTP đến {email}")
            return redirect('verify_otp')
        else:
            messages.error(request, "Hệ thống không thể gửi email. Vui lòng kiểm tra lại email!")
            
    return render(request, 'main/register.html')


def verify_otp(request):
    data = request.session.get('reg_temp')

    if not data:
        return redirect('register')

    if time.time() > data['exp_time']:
        messages.error(request, "Mã OTP hết hạn. Đăng ký lại.")
        del request.session['reg_temp']
        return redirect('register')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        if otp_input == data['otp']:
            try:
                user = Users.objects.create(
                    full_name=data['full_name'],
                    email=data['email'],
                    phone=data['phone'],
                    password_hash=data['password'],
                    role='customer'
                )
                Carts.objects.create(user=user, created_at=timezone.now())
                
                del request.session['reg_temp'] 
                messages.success(request, "Đăng ký thành công!")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Lỗi DB: {e}")
        else:
            messages.error(request, "Sai mã OTP!")

    return render(request, 'main/verify_otp.html')


def resend_otp(request):
    data = request.session.get('reg_temp')
    if not data:
        return redirect('register')

    if time.time() < data['next_resend']:
        wait_time = int(data['next_resend'] - time.time())
        messages.warning(request, f"Chờ {wait_time}s để gửi lại.")
        return redirect('verify_otp')

    new_otp = send_otp_email(data['email'])

    if new_otp:
        data['otp'] = new_otp
        data['next_resend'] = time.time() + 120
        request.session['reg_temp'] = data 
        
        messages.success(request, "Đã gửi mã mới.")
    else:
        messages.error(request, "Lỗi gửi mail.")

    return redirect('verify_otp')

def get_logout(request):
    request.session.flush()
    return redirect('index')

def generate_strong_password():
    length = 8
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()"

    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]

    all_chars = lower + upper + digits + special
    password += [random.choice(all_chars) for _ in range(length - 4)]

    random.shuffle(password)
    return ''.join(password)

def get_forgotpassword(request):
    if request.method == 'POST':
        email_input = request.POST.get('username', '').strip()
        cache_key = f"reset_pass_{email_input}"
        
        cache_key = f"reset_pass_{email_input}"
        if cache.get(cache_key):
            messages.error(request, "Bạn vừa yêu cầu đổi mật khẩu. Vui lòng thử lại sau 1 tiếng.")
            return render(request, 'main/forgotpassword.html')

        try:
            user = Users.objects.get(email__iexact=email_input)
            new_password_raw = generate_strong_password()
            
            user.password_hash = make_password(new_password_raw)
            user.save()

            subject = 'Cấp lại mật khẩu mới - Aroma Café'
            message = f'Chào {user.full_name},\n\nMật khẩu mới của bạn là: {new_password_raw}\n\nVui lòng đăng nhập và đổi lại mật khẩu ngay để bảo mật thông tin.'
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email_input],
                fail_silently=False
            )

            cache.set(cache_key, True, 3600)

            messages.success(request, "Mật khẩu mới đã được gửi vào email của bạn. Vui lòng kiểm tra hộp thư.")
            return redirect('login')

        except Users.DoesNotExist:
            print(f"DEBUG: Không tìm thấy email '{email_input}' trong DB") 
            messages.error(request, "Email này chưa được đăng ký trong hệ thống!")
        except Exception as e:
            print(e)
            messages.error(request, "Có lỗi xảy ra khi gửi email.")

    return render(request, 'main/forgotpassword.html')