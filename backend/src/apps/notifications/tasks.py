from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_mfa_email(email: str, code: str):
    send_mail(
        subject="Your Authentication Code",
        message=f"Your authentication code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
