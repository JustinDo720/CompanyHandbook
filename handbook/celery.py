from celery import Celery 
from django.conf import settings
import os 

# Tell Celery you're using Django Settings 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handbook.settings')

# Creating Celery Instance
celery_app = Celery('handbook')
celery_app.config_from_object(settings, namespace="CELERY")

# Broker Url 
celery_app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'

# Changing Timezone
celery_app.conf.timezone = "America/New_York"
celery_app.conf.enable_utc = False 

# Discovering @shared_task
celery_app.autodiscover_tasks()