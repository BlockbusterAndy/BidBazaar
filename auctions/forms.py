from django.forms import ModelForm, DateTimeField, ChoiceField
from django import forms

from .models import Listing

choices = [('Trading Cards', 'Trading Cards'), ('Comic Books', 'Comic Books'), ('Figurines', 'Figurines'), ('Collectibles', 'Collectibles'), ('Currency & Coins', 'Currency & Coins'), ('Other', 'Other')]

class ListingForm(ModelForm):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class':'border rounded p-2 w-full mt-2'}))
    category = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class':'border rounded p-2 w-full mt-2'}))
    description = forms.CharField(max_length=512, widget=forms.Textarea(attrs={'class':'border rounded p-2 w-full mt-2'}))
    starting_value = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.TextInput(attrs={'class':'border rounded p-2 w-full mt-2', 'type':"number", 'step':'0.01'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'border rounded p-2 w-full'}))
    # time = DateTimeField(input_formats=['%d/%m/%Y %H:%M'], widget=forms.DateTimeInput(attrs={'class':'border rounded p-2 w-full mt-2', 'type':'datetime-local'}))

    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'starting_value', 'image']