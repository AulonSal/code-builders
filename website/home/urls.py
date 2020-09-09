from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('announcements/', views.announcements, name='announcements'),

    # Auth
    path('portal/', views.portal, name='portal'),
    path('logout/', views.logoutuser, name='logout'),

]
