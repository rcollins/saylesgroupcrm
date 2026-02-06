"""
Send a test email to verify Anymail/Resend configuration.
"""
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Send a test email to verify email (Anymail/Resend) configuration."

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            nargs='?',
            default=None,
            help='Recipient email address (default: from DEFAULT_FROM_EMAIL if not set)',
        )

    def handle(self, *args, **options):
        to_email = options.get('email')
        if not to_email or not to_email.strip():
            self.stderr.write(
                self.style.ERROR('Provide a recipient: python manage.py send_test_email you@example.com')
            )
            return
        to_list = [to_email.strip()]

        try:
            send_mail(
                'RE CRM test email',
                'This is a test email from your RE CRM app. If you received it, Anymail/Resend is configured correctly.',
                settings.DEFAULT_FROM_EMAIL,
                to_list,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Test email sent to {to_list[0]}.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to send: {e}'))
