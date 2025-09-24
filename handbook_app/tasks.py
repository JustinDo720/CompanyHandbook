from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.management import call_command

"""
    We're going to create a custom Django Command for our task to call 
        - We use call_command to run something like: py manage.py django_custom_command 

    Shared tasks decorator is used with auto task discovery 
"""
@shared_task
def gen_faq():
    call_command('generate_faq')