from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='sign_up'),
    path('logout/',
         LogoutView.as_view(template_name='users/logout.html'),
         name='logout'),
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('password_reset_form/',
         PasswordResetView.as_view(
             template_name='users/password_reset_form.html'),
         name='password_reset_form'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'),
         name='password_reset_form_done'),
    path('password_change_form/',
         PasswordChangeView.as_view(
             template_name='users/change_form.html'),
         name='password_change_form'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view(
             template_name='users/change_done.html'), name='change_done'),
    path('auth/reset/<uid64>/<token>/', PasswordResetConfirmView.as_view(
         template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'),
        name='password_reset_complete'),
]
