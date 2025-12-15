from django.shortcuts import render

def get_about(request):
    return render(request, 'main/aboutUs.html')

def get_shippingPolicies(request):
    return render(request, 'main/shippingPolicies.html')

def get_termOfUse(request):
    return render(request, 'main/termOfUse.html')

def get_warrantyPolicies(request):
    return render(request, 'main/warrantyPolicies.html')

def get_help(request):
    return render(request, 'main/help.html')