import uuid

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import User, Pekerja, Pengguna

class PenggunaRegisterForm(UserCreationForm):
    GENDER_CHOICES = (
        ('Laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan')
    )
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name', max_length=50)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone_number = forms.CharField(widget=forms.TextInput(), required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'birth_date', 'address', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.gender = self.cleaned_data['gender']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.address = self.cleaned_data['address']
        user.is_pengguna = True
        user.save()
        pengguna = Pengguna.objects.create(user=user)
        return user

class PekerjaRegisterForm(UserCreationForm):
    GENDER_CHOICES = (
        ('Laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan')
    )
    BANK_CHOICES = (
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('Virtual Account BCA', 'Virtual Account BCA'),
        ('Virtual Account BNI', 'Virtual Account BNI'),
        ('Virtual Account Mandiri', 'Virtual Account Mandiri'),
    )
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name', max_length=50)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone_number = forms.CharField(widget=forms.TextInput(), required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    bank = forms.ChoiceField(choices=BANK_CHOICES)
    bank_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    npwp = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'birth_date', 'address', 'password1', 'password2')



    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        user.gender = self.cleaned_data['gender']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.address = self.cleaned_data['address']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_pekerja = True
        user.save()
        pekerja = Pekerja.objects.create(user=user, bank=self.cleaned_data['bank'], bank_number=self.cleaned_data['bank_number'], npwp=self.cleaned_data['npwp'], image_url=self.cleaned_data['image_url'])
        return user

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'phone_number', 'birth_date', 'address']

class UpdatePekerjaForm(forms.ModelForm):
    class Meta:
        model = Pekerja
        fields = ['bank', 'bank_number', 'npwp', 'image_url']

class UserLoginForm(forms.Form):
    phone_number = forms.CharField(label="Phone Number", widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)