from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('iframe-contact/', views.contact_frame, name='contact-frame'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('announcements/', views.announcements, name='announcements'),

    # Auth
    path('logout/', views.logoutuser, name='logout'),

]
