import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SPA_comments.settings')

app = Celery('SPA_comments', broker='redis://redis:6379/0')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

app.conf.beat_schedule = {
    'count_comments': {
        'task': 'comments.tasks.get_jwt_token',
        'schedule': crontab(minute='*')
    }

}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
