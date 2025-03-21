from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user_email, user_name, event_name):
    """
    Send a welcome email to the user after successful registration
    """
    subject = f'Welcome to {event_name}!'
    message = f"""Dear {user_name},

Thank you for registering for {event_name}! We're excited to have you join us.

Your registration has been successfully processed. We'll keep you updated with any important information regarding the camp.

Best regards,
AIBF Team"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
