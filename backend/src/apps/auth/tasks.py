import logging

from allauth.account.models import EmailAddress
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
        logging.error("Failed to send email: %s", str(error))


@shared_task
def check_email_confirmation(email_address_id: int):
    try:
        email_address = EmailAddress.objects.select_related("user").get(
            id=email_address_id
        )
        if not email_address.verified:
            email_address.emailconfirmation_set.prefetch_related(
                "email_address"
            ).all().delete()
    except EmailAddress.DoesNotExist: # noqa
        pass
