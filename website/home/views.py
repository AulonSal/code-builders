from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def error404(request, exception=None):
    return render(request, 'handler/error.html', status=404)

def home(request):
	return render(request, 'home/home.html')

@login_required
def dashboard(request):
	return render(request, 'home/dashboard.html')

@login_required
def profile(request):
	return render(request, 'home/profile.html')

def portal(request):
    if request.method == 'GET':
        return render(request, 'sign_in/sign.html', {'form':UserCreationForm()})
    else:
        if 'signup' in request.POST:
            
            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                    user.save()
                    login(request, user)
                    return redirect('/')
                except IntegrityError:
                    return render(request, 'sign_in/sign.html', {'form':UserCreationForm(), 'error':'Unexpected error occurred'})
            else:
                return render(request, 'sign_in/sign.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})
        else:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'sign_in/sign.html', {'form':AuthenticationForm(), 'error':'Invalid Credentials.'})
            else:
                login(request, user)
                return redirect('/')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/')
