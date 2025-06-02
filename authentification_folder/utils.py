from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import jwt
from datetime import datetime, timedelta
def send_verification_email(user):
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now() + timedelta(hours=24),
        'type': 'email_verification'
    }, settings.SECRET_KEY, algorithm='HS256')
    subject = "Reset your password"
    message = f"Hi {user.email},\n\nPlease reset your password by clicking the link below:\n\n"
    message += f"http://127.0.0.1:8000/api/v1/reset-password?token={token}\n\n"
    message += "This link is valid for 24 hour.\n\nThank you,\nALGECOM Team"
    try:
        send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
    except Exception as e:
                # Log the error but do not reveal to the client
                print(f"Error sending password reset email: {e}")
                return Response(
                    {"error": "Failed to send password reset email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
                
from django.urls import reverse
def send_password_reset_email(user):
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(datetime.timezone.utc) + timedelta(hours=1),
        'type': 'password_reset'
    }, settings.SECRET_KEY, algorithm='HS256')

    reset_url = "http://127.0.0.1:8000/api/v1/" + reverse('password-reset-confirm') + f'?token={token}'
    
    subject = "Password Reset Request"
    message = f"Click to reset password: {reset_url}"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )