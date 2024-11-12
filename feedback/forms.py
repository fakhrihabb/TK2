from django import forms
from .models import Testimoni

class TestimoniForm(forms.ModelForm):
    class Meta:
        model = Testimoni
        fields = ['user', 'rating', 'comment']
        widgets = {
            'user': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}), 
            'comment': forms.Textarea(attrs={'placeholder': 'Your Feedback'}),
        }
