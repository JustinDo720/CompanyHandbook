from django.core.management import BaseCommand
from companies.models import Quota
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    """
        Reset all the quotas that were used
    """

    def handle(self, *args, **kwargs):
        # Filter all the quota that has an amount < 5 (our default)
        default_quota = 5
        used_quotas = Quota.objects.filter(amount__lt=5)

        amt_of_reset = 0
        for quota in used_quotas:
            quota.amount = 5
            quota.save()
            amt_of_reset += 1
        
        if amt_of_reset > 0:
            send_mail(
                subject='Quota Reset - Daily',
                message=f'Hello! Premium user(s) quota has been reset. Amount: {amt_of_reset} quota(s)...',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_RECIPIENT, settings.EMAIL_HOST_USER],
                fail_silently=True
            )

