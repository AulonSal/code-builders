import razorpay
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from home.models import TeamMember, Participant

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

    # SIGNUP Request
    if request.POST['password'] != request.POST['password-confirmation']:
        return render(request, 'sign_in/sign.html', {'signup_error': 'Passwords did not match'})

    username = request.POST['username']
    password = request.POST['password']
    referral_code = request.POST['referral-code']
    email = request.POST['email']
    contact_number = request.POST['contact-no']

    # Referral Code validity check
    if referral_code and not (referrer := TeamMember.objects.filter(referral_code=referral_code)):
        return render(request, 'sign_in/sign.html', {'signup_error': 'Invalid Referral Code'})

    # Referral Code
    referral_code, referrer = (None, None) if not referral_code else (referral_code, referrer[0])

    # Transaction Details
    # TODO: MOVE to db


    discount_multiplier = 0.8

    general_details = {
        'amount': 1000,
        'currency': 'INR',
        'notes': {
            'Purpose': 'EVENT PASS',
        },
    }

    general_details['amount'] = general_details['amount'] * discount_multiplier if referral_code else \
        general_details['amount']

    client_details = {
        'receipt': f"{username}.1"
    }

    # Send order to Razorpay and receive id and status
    response = client.order.create({**general_details, **client_details})
    order_id = response['id']
    order_status = response['status']

    # If successful order, show order-confirmation
    if order_status == 'created':
        # Razorpay data
        context = dict(name=username, contact_number=contact_number, email=email, **general_details)
        context['order_id'] = order_id
        context['data_key'] = settings.PAY_KEY_ID

        # TODO: Figure out how to pass user details to confirm view for creation
        # Pass the details for new user creation
        new_user = dict(
            username=username,
            password=password,
            email=email,
            referrer=referrer,
            contact_number=contact_number,
        )
        request.session['new_user'] = new_user

        # Order payment
        return render(request, 'payments/confirm_order.html', context)
        print('\n\n\nresponse: ', response, type(response))

    return render(request, 'sign_in/sign.html', {'signup_error': 'Order not created'})


@require_http_methods(["POST"])
def payment_status(request):
    response = request.POST

    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    new_user = request.session['new_user']
    # VERIFYING SIGNATURE
    try:
        status = client.utility.verify_payment_signature(params_dict)
        user = User.objects.create_user(
            username=new_user['username'],
            password=new_user['password'],
            email=new_user['email'],
        )
        user.save()

        participant = Participant.objects.create(
            user=user,
            referrer=new_user['referrer'],
            contact_number=new_user['contact_number'],
        )
        participant.save()
        return render(request, 'payments/order_summary.html', {'status': 'Payment Successful'})

    except IntegrityError:
        return redirect('portal')  # render(request, 'sign_in/sign.html',{'signup_error': 'Unexpected error occurred'})

