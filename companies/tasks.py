from __future__ import unicode_literals, absolute_import
from celery import shared_task
from django.core.management import call_command

@shared_task
def reset_quota():
    call_command('reset_quota')