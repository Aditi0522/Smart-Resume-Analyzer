import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMART.settings')

app = Celery('SMART')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

