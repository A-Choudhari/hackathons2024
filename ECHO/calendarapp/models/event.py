from datetime import datetime
from django.db import models
from django.urls import reverse

from calendarapp.models import EventAbstract
from accounts.models import User
from datetime import timedelta, timezone
from twilio.rest import Client


class EventManager(models.Manager):
    """ Event manager """

    def get_all_events(self, user):
        events = Event.objects.filter(user=user, is_active=True, is_deleted=False)
        return events

    def get_running_events(self, user):
        running_events = Event.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            end_time__gte=datetime.now().date(),
        )
        return running_events


class Event(EventAbstract):
    """ Event model """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    end_time = models.DateTimeField()
    #start_time = models.DateTimeField()

    objects = EventManager()

    def __str__(self):
        return self.title


    def toDict(self):
        return [self.id, self.title, self.description, self.difficulty, self.is_active, self.end_time]

    def get_absolute_url(self):
        return reverse("calendarapp:event-detail", args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse("calendarapp:event-detail", args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'

    def send_message(self, *args, **kwargs):
        # Calculate the reminder time
        reminder_time = self.end_time - timedelta(minutes=30)

        # Use timezone aware datetime for comparison
        current_time = timezone.now()

        if reminder_time <= current_time <= self.end_time:
            account_sid = ""
            auth_token = ""
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f"Hi,this is ECHO!\nThis is a reminder for {self.title} which is at {self.end_time} \n The difficulty of the task is {self.difficulty}. Good Luck!",
                from_="",
                to=f"{self.user.phone_number}"
            )

            call = client.calls.create(
                twiml=f"<Respose><Say>Hi,this is !\nThis is a reminder for {self.title} which is at {self.end_time} \n The difficulty of the task is {self.difficulty}. Good Luck!</Say></Response>",
                from_="",
                to=f"{self.user.phone_number}"
            )
            print(message.sid)
            print(call.sid)
        return super().save(*args, **kwargs)