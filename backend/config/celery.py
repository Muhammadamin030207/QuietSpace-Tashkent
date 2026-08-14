from celery import Celery
from django.conf import settings

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("quietspace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
