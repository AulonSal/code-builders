import logging

import razorpay
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
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

        # If user is participant and has not paid, delete user
        try:
            participant = user.participant

            if participant.paid is False:
                user.delete()
                return render(request, 'sign_in/sign.html',
                              {'signin_error': 'Invalid Credentials.'})

        except ObjectDoesNotExist:
            pass

        login(request, user)
        return redirect('/')

    # SIGNUP request
    name = request.POST['name']
    password = request.POST['password']
    password_confirmation = request.POST['password-confirmation']
    referral_code = request.POST['referral-code']
    email = request.POST['email']
    username = email
    contact_number = request.POST['contact-no']

    # Password confirmation
    if password != password_confirmation:
        return render(request, 'sign_in/sign.html', {'signup_error': 'Passwords did not match'})

    # Throw away old temp user if payment never happened
    try:
        temp_user = User.objects.get(email=email)
        if temp_user.participant.paid is False:
            temp_user.delete()
    except ObjectDoesNotExist:
        pass

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
            email=email,
        )

        participant_details = dict(
            referrer=referrer,
            contact_number=contact_number,
        )

        user = User(**user_details)
        user.set_password(password)
        participant = Participant(**participant_details)

        # Validate model instances
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
        'receipt': f"{email[:35]}.1"
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

        # Create Participant and user
        user.save()
        participant.user = user
        participant.paid = False
        participant.order_id = order_id
        participant.save()

        # Log before payments
        pre_log = f"""BEFORE_PAYMENT: User Details: {user_details}\n Participant Details: {participant_details}"""
        logger.info(pre_log)

        # Order payment
        return render(request, 'payments/confirm_order.html', context)

    return render(request, 'sign_in/sign.html', {'signup_error': 'Order not created'})


@require_http_methods(["POST"])
@csrf_exempt
def payment_status(request):
    response = request.POST

    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature'],
    }

    info_log = f"""AFTER_PAYMENT: Razorpay details: {params_dict}"""

    logger.info(info_log)
    logger.info("If no AFTER_PAYMENT before this, SNAFU")

    # VERIFYING SIGNATURE
    try:
        status = client.utility.verify_payment_signature(params_dict)

    # Invalid order/payment
    except SignatureVerificationError:
        # Delete temp_user if it exists
        try:
            participant = Participant.objects.get(order_id=params_dict['razorpay_order_id'])

            # Make sure it's not a malicious request to delete user
            if participant.paid is False:
                user = participant.user
                user.delete()

        except ObjectDoesNotExist:
            pass

        return render(request, 'payments/order_summary.html', {'status': 'Payment Failed'})

    # Turn paid to true for Participant
    try:
        participant = Participant.objects.get(order_id=params_dict['razorpay_order_id'])
        participant.paid = True
        participant.save()

    # TODO: Add message to user asking them to contact us
    except ObjectDoesNotExist:
        logger.error("SNAFU, Payment went through but user with order id doesn't exist")
        return render(request, 'payments/order_summary.html', {'status': 'Payment Failed'})

    return render(request, 'payments/order_summary.html', {'status': 'Payment Successful'})
