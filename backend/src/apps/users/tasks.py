import logging

from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message, from_email, recipient_list, html_message=None):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logging.info("Email sent successfully")
    except Exception as error:
        logging.error("Failed to send email: $s", str(error))
