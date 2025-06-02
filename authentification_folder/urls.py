from django.urls import path
from .views import PasswordResetConfirmView, PasswordResetRequestView, RegisterView, LoginView, UserLogoutView, VerifyEmailView
from rest_framework_simplejwt.views import TokenRefreshView

auth_path='auth/'
urlpatterns = [
    path(f'{auth_path}register/', RegisterView.as_view(), name='register'),
    path(f'{auth_path}login/', LoginView.as_view(), name='login'),
    path(f'{auth_path}token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path(f'{auth_path}verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    
    path(f'{auth_path}logout/', UserLogoutView.as_view(), name='logout'),
    path(f'{auth_path}password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path(f'{auth_path}password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

