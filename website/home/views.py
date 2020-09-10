from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


def home(request):
    return render(request, 'home/home.html')


@login_required
def dashboard(request):
    return render(request, 'home/dashboard.html')


@login_required
def profile(request):
    return render(request, 'home/profile.html')


@login_required
def announcements(request):
    return render(request, 'home/announcements.html')


@require_http_methods(["POST"])
@login_required
def logoutuser(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Logout successful')
    return redirect('/')
