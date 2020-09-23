from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_http_methods

from .models import Announcement, TeamMember, EventCategory, User, Participant


def home(request):
    event_categories = EventCategory.objects.all()
    return render(request, 'home/home.html', dict(
        event_categories=event_categories,
    ))


def contact_us(request):
    return render(request, 'home/contact-us.html')


def policy(request):
    return render(request, 'home/policies.html')


def refund_policy(request):
    return render(request, 'home/refundPolicy.html')


def terms_conditions(request):
    return render(request, 'home/termsAndConditions.html')


def privacy_policy(request):
    return render(request, 'home/privacyPolicy.html')


@xframe_options_sameorigin
def contact_frame(request):
    return render(request, 'home/contact-template.html')


@login_required
def dashboard(request):
    return render(request, 'home/dashboard.html')


@login_required
def profile(request):
    try:
        participants = request.user.teammember.participant_set.filter(paid=True)
        referral_count = participants.count()
    except ObjectDoesNotExist:
        referral_count = None
    return render(request, 'home/profile.html', dict(
        referral_count=referral_count,
    ))


@login_required
def teammember_dashboard(request, pk):
    if not (request.user.id == pk or request.user.is_staff):
        print('fucked')
        raise PermissionDenied

    try:
        user = User.objects.get(id=pk)
        participants = user.teammember.participant_set.filter(paid=True)
        referral_count = participants.count()
    except ObjectDoesNotExist:
        print('fucked backwards')
        raise PermissionDenied

    return render(request, 'home/team_dashboard.html', dict(
        referral_count=referral_count,
        participants=participants,
    ))


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


@staff_member_required
def admindashboard(request):
    teammembers = TeamMember.objects.annotate(referrals=Count('participant', filter=Q(participant__paid=True)))
    all_participants = Participant.filter_paid()
    total_participants = all_participants.count()
    nonreferral_participants = all_participants.filter(referrer=None).count()
    total_referrals = total_participants - nonreferral_participants

    return render(request, 'home/adminDashboard.html', dict(
        teammembers=teammembers,
        total_participants=total_participants,
        nonreferral_participants=nonreferral_participants,
        total_referrals=total_referrals,
    ))
