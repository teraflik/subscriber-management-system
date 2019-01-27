from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.http import HttpResponse

from .models import Address, Subscription, Label
from .forms import SubscriptionForm

def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return LoginView.as_view(template_name='login.html')(request)

def createSub(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
    else:
        form = SubscriptionForm()
    return render(request, 'create_sub.html', {'form': form})