from django.shortcuts import render, redirect
from django.utils import timezone
from ..models import Contacts, Users  

def get_help(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login') 

    context = {}

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        try:

            current_user = Users.objects.get(id=user_id)
            
            Contacts.objects.create(
                user=current_user,
                full_name=name,
                email=email,
                message=message,
                sent_at=timezone.now()
            )

            context['success_msg'] = "Tin nhắn của bạn đã được gửi thành công."
            
        except Users.DoesNotExist:
            return redirect('login')


    return render(request, 'main/help.html', context)