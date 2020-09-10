from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import Announcement
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.clickjacking import xframe_options_sameorigin

def home(request):
    return render(request, 'home/home.html')

def contact_us(request):
    return render(request, 'home/contact-us.html')

@xframe_options_sameorigin
def contact_frame(request):
    return render(request, 'home/contact-template.html')

@login_required
def dashboard(request):
    return render(request, 'home/dashboard.html')


@login_required
def profile(request):
    try:
        referral_count = request.user.teammember.participant_set.count()
    except ObjectDoesNotExist:
        referral_count = None
    return render(request, 'home/profile.html', {'referral_count': referral_count})


@login_required
def announcements(request):
    announcements_ = Announcement.objects.all().order_by('created_on')
    return render(request, 'home/announcements.html', {'announcements': announcements_})


@require_http_methods(["POST"])
@login_required
def logoutuser(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Logout successful')
    return redirect('/')
