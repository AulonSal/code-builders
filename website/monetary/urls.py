from django.urls import path

from . import views

urlpatterns = [
    # Auth
    path('portal/', views.portal, name='portal'),

    # Payments
    path('payment-confirmed/', views.payment_status, name='payment_status', )
]
