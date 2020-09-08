from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

     # Auth
    path('portal/', views.portal, name='portal'),
    path('logout/', views.logoutuser, name='logout'),

    ]

