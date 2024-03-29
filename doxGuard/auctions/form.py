from django import forms
from .models import Image, Video


class ImageUploadForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'type': 'file', 'id':'input-file', 'required':'required'}))

    class Meta:
        model = Image
        fields = ['image', 'user']


class VideoUploadForm(forms.ModelForm):
    video = forms.FileField(widget=forms.ClearableFileInput(attrs={'accept': 'video/*', 'type': 'file', 'id':'input-file', 'required':'required'}))

    class Meta:
        model = Video
        fields = ['video', 'user']