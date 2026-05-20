from django.urls import path

from .views import (
    AuthEventListView,
    LoginView,
    MFADisableView,
    MFAEnableView,
    MFAVerifyView,
    LogoutView,
    RegisterView,
    RefreshTokenView,
)

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/mfa/enable/', MFAEnableView.as_view(), name='mfa-enable'),
    path('auth/mfa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),
    path('auth/mfa/disable/', MFADisableView.as_view(), name='mfa-disable'),
    path('auth/events/', AuthEventListView.as_view(), name='auth-events'),
]
