from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

class PenggunaRegistrationForm(UserCreationForm):
    gender = forms.ChoiceField(choices=(('L', 'Male'), ('P', 'Female')),)
    phone_number = forms.CharField(max_length=20)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ('username', 'gender', 'phone_number', 'birth_date', 'address')
    def save(self, commit=True):
        user = super(PenggunaRegistrationForm, self).save(commit=False)
        user.gender = self.cleaned_data['gender']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.address = self.cleaned_data['address']

        if commit:
            user.save()
        return user
