from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("image_blur", views.image_blur, name="image_blur"),
    path("video_blur", views.video_blur, name="video_blur"),
    path("liveCapture_blur", views.liveCapture_blur, name="liveCapture_blur"),
    path("stream_capture", views.stream_capture, name="stream_capture"),
    path("audio_capture", views.audio_capture, name="audio_capture"),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
