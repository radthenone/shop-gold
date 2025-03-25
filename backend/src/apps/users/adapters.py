import logging
import uuid
from datetime import timedelta

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.headless.tokens.base import AbstractTokenStrategy
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.tasks import send_email_task


class AccountAdapter(DefaultAccountAdapter):
    def render_mail(self, template_prefix, email, context, headers=None):
        to = [email] if isinstance(email, str) else email
        subject = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        from_email = self.get_from_email()

        template_name = f"{template_prefix}.html"
        html_body = render_to_string(template_name, context).strip()

        msg = EmailMultiAlternatives(
            subject=subject,
            body=html_body,
            from_email=from_email,
            to=to,
            headers=headers,
        )
        msg.attach_alternative(html_body, "text/html")
        return msg

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        ctx = {
            "user": emailconfirmation.email_address.user,
            "code": emailconfirmation.key,
            "current_site": get_current_site(request),
            "sent_at": timezone.now(),
            "request": request,
        }

        template_prefix = "account/email/email_confirmation_signup"
        self.send_mail(template_prefix, emailconfirmation.email_address.email, ctx)

    def send_mail(self, template_prefix: str, email: str, context: dict) -> None:
        logging.info(
            "send_mail called with template: %s, email: %s", template_prefix, email
        )
        request = context.get("request")
        ctx = {
            "request": request,
            "email": email,
            "current_site": get_current_site(request) if request else None,
        }
        ctx.update(context)

        msg = self.render_mail(template_prefix, email, ctx)

        html_message = None
        if msg.alternatives:
            html_message = msg.alternatives[0][0]

        task = send_email_task.delay(
            subject=msg.subject,
            message=msg.body,
            from_email=msg.from_email,
            recipient_list=msg.to,
            html_message=html_message or msg.body,
        )
        logging.info("Email task created: %s", task.id)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        logging.info(
            "send_confirmation_mail called for user: %s",
            emailconfirmation.email_address.user,
        )
        ctx = {
            "user": emailconfirmation.email_address.user,
            "code": emailconfirmation.key,
            "current_site": get_current_site(request),
            "sent_at": emailconfirmation.sent,
            "request": request,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
