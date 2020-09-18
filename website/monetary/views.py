import logging

import razorpay
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from razorpay.errors import SignatureVerificationError

from home.models import TeamMember, Participant

logger = logging.getLogger('website.monetary')
client = razorpay.Client(auth=(settings.PAY_KEY_ID, settings.PAY_SECRET_KEY))


def portal(request):
    # TODO: Move to decorator
    # Redirect logged in users away
    logged_in = request.user.is_authenticated
    if logged_in:
        return redirect('/')

    # GET Page
    if request.method == 'GET':
        return render(request, 'sign_in/sign.html')

    # TODO: Refactor
    # SIGNIN request
    if 'signup' not in request.POST:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        # Throw invalid user back
        if user is None:
            return render(request, 'sign_in/sign.html',
                          {'signin_error': 'Invalid Credentials.'})

        login(request, user)
        return redirect('/')

    name = request.POST['name']
    password = request.POST['password']
    password_confirmation = request.POST['password-confirmation']
    referral_code = request.POST['referral-code']
    email = request.POST['email']
    username = email
    contact_number = request.POST['contact-no']

    # SIGNUP Request
    if password != password_confirmation:
        return render(request, 'sign_in/sign.html', {'signup_error': 'Passwords did not match'})

    if User.objects.filter(email=email):
        return render(request, 'sign_in/sign.html', {'signup_error': 'Email already registered'})

    # Referral Code validity check
    if referral_code and not (referrer := TeamMember.objects.filter(referral_code=referral_code)):
        return render(request, 'sign_in/sign.html', {'signup_error': 'Invalid Referral Code'})

    # Referral Code
    referral_code, referrer = (None, None) if not referral_code else (referral_code, referrer[0])

    # Create New User & Participant instances
    try:
        user_details = dict(
            username=username,
            first_name=name,
            password=password,
            email=email,
        )

        participant_details = dict(
            referrer=referrer,
            contact_number=contact_number,
        )

        user = User(**user_details)
        participant = Participant(**participant_details)

        # Validating model instances
        user.full_clean(validate_unique=True)
        participant.clean_fields(exclude=('user',))

    except (IntegrityError, ValidationError):
        return render(request, 'sign_in/sign.html', {'signup_error': 'Invalid User Details'})

    # Transaction Details
    # TODO: MOVE to db
    discount = 33000

    general_details = {
        'amount': 210000,
        'currency': 'INR',
        'notes': {
            'Purpose': 'EVENT PASS',
        },
    }

    general_details['amount'] = (general_details['amount'] - discount) if referral_code else \
        general_details['amount']

    client_details = {
        'receipt': f"{username}.1"
    }

    # Send order to Razorpay and receive id and status
    response = client.order.create({**general_details, **client_details})
    order_id = response['id']
    order_status = response['status']

    # Upon successful order, show order-confirmation
    if order_status == 'created':
        # Razorpay data
        context = dict(name=name, contact_number=contact_number, email=email, **general_details)
        context['order_id'] = order_id
        context['data_key'] = settings.PAY_KEY_ID

        # Pass referrer id, skip serialisation
        referrer_id = referrer.id if referrer else None
        request.session['new_user'] = (user_details, contact_number, referrer_id)

        # Log before payments
        user_log_details = {k: v for k, v in user_details if k != 'password'}
        pre_log = f"""BEFORE_PAYMENT: User Details: {user_log_details}\n Participant Details: {participant_details}"""
        logger.info(pre_log)

        # Order payment
        return render(request, 'payments/confirm_order.html', context)

    return render(request, 'sign_in/sign.html', {'signup_error': 'Order not created'})


@require_http_methods(["POST"])
def payment_status(request):
    response = request.POST

    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature'],
    }

    user_details, contact_number, referrer_id = request.session['new_user']
    referrer = TeamMember.objects.get(id=referrer_id) if referrer_id else None

    user_log_details = {k: v for k, v in user_details if k != 'password'}

    info_log = f"""AFTER_PAYMENT: User Details: {user_log_details} \nContact Number: {contact_number} \nReferrer Id: {referrer_id} \n\
    Razorpay details: {params_dict}"""

    logger.info(info_log)

    # VERIFYING SIGNATURE
    try:
        status = client.utility.verify_payment_signature(params_dict)
    except SignatureVerificationError:
        return render(request, 'payments/order_summary.html', {'status': 'Payment Failed'})

    user = User.objects.create_user(**user_details)
    Participant.objects.create(contact_number=contact_number, referrer=referrer, user=user)

    return render(request, 'payments/order_summary.html', {'status': 'Payment Successful'})
