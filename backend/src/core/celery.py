import os

from celery import Celery

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.dev")


app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
