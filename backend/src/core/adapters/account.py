import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import get_adapter as mfa_adapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from apps.users.tasks import send_email_task


class AccountAdapter(DefaultAccountAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        verify_url = reverse_lazy("user-verify-email", args=[emailconfirmation.key])
        url = settings.FRONTEND_URL + verify_url
        ctx = {
            "user": emailconfirmation.email_address.user,
            "code": emailconfirmation.key,
            "current_site": get_current_site(request),
            "url": url,
            "qr_code": mfa_adapter().build_totp_svg(url=url),
            "sent_at": emailconfirmation.sent,
            "request": request,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
