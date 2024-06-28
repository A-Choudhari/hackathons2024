from django.urls import path

from . import views
from .views.other_views import to_do_list, daily_check, journals, user_transcript, stream, end_item
app_name = "calendarapp"


urlpatterns = [
    path("calendar/", views.CalendarViewNew.as_view(), name="calendar"),
    path("calenders/", views.CalendarView.as_view(), name="calendars"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),
    path("event/new/", views.create_event, name="event_new"),
    path("daily/checkIn/", daily_check, name="daily_check"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path("journals", journals, name="journals"),
    path("stream", stream, name="stream"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path("to_do_list", to_do_list, name="to_do_list"),
    path("end_item", end_item, name="end_item"),
    path("user_transcript", user_transcript, name="user_transcript"),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path(
        "event/<int:pk>/remove",
        views.EventMemberDeleteView.as_view(),
        name="remove_event",
    ),
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "running-event-list/",
        views.RunningEventsListView.as_view(),
        name="running_events",
    ),
]
