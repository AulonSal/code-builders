import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import TeamMember, Participant

# Payments
client = razorpay.Client(auth=(settings.PAY_KEY_ID, settings.PAY_SECRET_KEY))


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


def portal(request):
    logged_in = request.user.is_authenticated

    if logged_in:
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'sign_in/sign.html')

    if 'signup' not in request.POST:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'sign_in/sign.html',
                          {'signin_error': 'Invalid Credentials.'})
        else:
            login(request, user)
            return redirect('/')

    if request.POST['password'] != request.POST['password-confirmation']:
        return render(request, 'sign_in/sign.html',
                      {'signup_error': 'Passwords did not match'})

    username = request.POST['username']
    password = request.POST['password']
    referral_code = request.POST['referral-code']
    email = request.POST['email']
    contact_number = request.POST['contact-no']

    # Referral Code check
    if referral_code and not (referrer := TeamMember.objects.filter(referral_code=referral_code)):
        return render(request, 'sign_in/sign.html', {'signup_error': 'Invalid Referral Code'})

    referral_code = None if not referral_code else referral_code
    referrer = referrer[0] if referral_code else None

    # All details validated

    # TODO: MOVE to db
    common_details = {
        'amount': 1000,
        'currency': 'INR',
        'notes': {
            'Purpose': 'EVENT PASS',
        },
        'payment_capture': '0',
    }

    discount_multiplier = 0.8
    common_details['amount'] = common_details['amount'] * discount_multiplier if referral_code else common_details['amount']

    client_details = {
        'receipt': f"{username}.1"
    }

    response = client.order.create({**common_details, **client_details})
    order_id = response['id']
    order_status = response['status']

    if order_status == 'created':
        # Serve data for user convinience
        # Razorpay data
        context = dict(name=username, phone=contact_number, email=email, **common_details)
        context['order_id'] = order_id
        context['data_key'] = settings.PAY_KEY_ID

        # TODO: Figure out how to pass user details to confirm view for creation
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )
            user.save()

            participant = Participant.objects.create(
                user=user,
                referrer=referrer,
                contact_number=contact_number,
            )
            participant.save()

        # No idea if it works
        except IntegrityError:
            return render(request, 'sign_in/sign.html',
                          {'signup_error': 'Unexpected error occurred'})

        # Order payment
        return render(request, 'payments/confirm_order.html', context)
        # print('\n\n\nresponse: ',response, type(response))

    return render(request, 'sign_in/sign.html', {'signup_error': 'Unknown error at the first step'})


def payment_status(request):

    response = request.POST

    params_dict = {
        'razorpay_payment_id' : response['razorpay_payment_id'],
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_signature' : response['razorpay_signature']
    }

    # VERIFYING SIGNATURE
    try:
        status = client.utility.verify_payment_signature(params_dict)
        return render(request, 'payments/order_summary.html', {'status': 'Payment Successful'})
    except:
        return render(request, 'payments/order_summary.html', {'status': 'Payment Faliure!!!'})


@require_http_methods(["POST"])
@login_required
def logoutuser(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Logout successful')
    return redirect('/')
