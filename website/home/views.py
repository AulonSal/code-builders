from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages


def home(request):
    return render(request, 'home/home.html')


@login_required
def dashboard(request):
    return render(request, 'home/dashboard.html')


@login_required
def profile(request):
    return render(request, 'home/profile.html')


def portal(request):
    logged_in = request.user.is_authenticated
    if request.method == 'GET' and not logged_in:
        return render(request, 'sign_in/sign.html', {'form': UserCreationForm()})
    elif logged_in:
        return redirect('/')
    else:
        if 'signup' in request.POST:

            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'], email=request.POST['email'])
                    user.save()
                    login(request, user)
                    return redirect('/')
                except IntegrityError:
                    return render(request, 'sign_in/sign.html',
                                  {'form': UserCreationForm(), 'error': 'Unexpected error occurred'})
            else:
                return render(request, 'sign_in/sign.html',
                              {'form': UserCreationForm(), 'error': 'Passwords did not match'})
        else:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'sign_in/sign.html',
                              {'form': AuthenticationForm(), 'error': 'Invalid Credentials.'})
            else:
                login(request, user)
                return redirect('/')


@require_http_methods(["POST"])
@login_required
def logoutuser(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Logout successful')
    return redirect('/')
