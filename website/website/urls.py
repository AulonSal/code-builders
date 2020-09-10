from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from home import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # AUTH
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='auth/reset_link.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/set_pass.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/reset_done.html'),
         name='password_reset_complete'),
    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(template_name='auth/reset_pass.html'),
         name='password_reset'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('monetary.urls')),
]
