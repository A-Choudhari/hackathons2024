from celery import shared_task
from django.utils import timezone
from .models.event import Event
from datetime import timedelta


@shared_task
def send_event_reminders():
    now = timezone.now() + timedelta(minutes=30)
    events = Event.objects.filter(is_active=True, end_time=now)
    for event in events:
        event.send_message()
