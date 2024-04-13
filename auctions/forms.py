from django.forms import ModelForm
from django import forms

from .models import Listing

class ListingForm(ModelForm):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class':'form-control'}))
    category = forms.CharField(max_length=32, required="False", widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(max_length=512, widget=forms.Textarea(attrs={'class':'form-control'}))
    starting_value = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.TextInput(attrs={'class':'form-control', 'type':"number", 'step':'0.01'}))
    image = forms.ImageField(required="False", widget=forms.FileInput(attrs={'class':'form-control-file'}))
    
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'starting_value', 'image']