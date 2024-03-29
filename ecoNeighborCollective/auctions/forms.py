from django import forms
from .models import Listings, Trash


class ImageUploadForm(forms.ModelForm):
    custom_input = forms.FloatField(widget=forms.TextInput(attrs={'type': 'number', 'step': '0.01', 'class':'form-control', 'aria-describedby':'inputGroup-sizing-default', 'required':'required', 'placeholder':'Minimum Bid'}), required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'type':'text','class':'form-control', 'aria-describedby':'inputGroup-sizing-lg', 'required':'required'}))
    image_url = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id':'inputGroupFile02', 'required':'required'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40, 'class': 'form-control', 'aria_label': 'Description', 'required':'required'}))

    class Meta:
        model = Listings
        fields = ['description', 'owner', 'title', 'price', 'image_url']


class TrashForm(forms.ModelForm):
    location = forms.CharField(widget=forms.TextInput(attrs={'type':'text','name':'location_form', 'class':'form-control',
                                                             'aria-describedby':'button-addon1', 'required':'required'}))
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id':'inputGroupFile02', 'required':'required', 'id':'location'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 40, 'class': 'form-control', 'aria_label': 'Description', 'required':'required'}))

    class Meta:
        model = Trash
        fields = ['user', 'location', 'description', 'image']
