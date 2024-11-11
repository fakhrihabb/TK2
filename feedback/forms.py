from django import forms
from .models import Testimoni

class TestimoniForm(forms.ModelForm):
    class Meta:
        model = Testimoni
        fields = ['user', 'rating', 'comment']
        widgets = {
            'user': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'placeholder': 'Your Feedback'}),
        }
