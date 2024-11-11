from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User, Pekerja, Pengguna

class PenggunaRegisterForm(UserCreationForm):
    GENDER_CHOICES = (
        ('Laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan')
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone_number = forms.CharField(widget=forms.TextInput(), required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        # user.gender = self.cleaned_data['gender']
        # user.phone_number = self.cleaned_data['phone_number']
        # user.birth_date = self.cleaned_data['birth_date']
        # print(self.cleaned_data['birth_date'])
        # user.address = self.cleaned_data['address']
        user.is_pengguna = True
        user.save()
        pengguna = Pengguna.objects.create(user=user, gender=self.cleaned_data['gender'], phone_number=self.cleaned_data['phone_number'], birth_date=self.cleaned_data['birth_date'], address=self.cleaned_data['address'])
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
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone_number = forms.CharField(widget=forms.TextInput(), required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    bank = forms.ChoiceField(choices=BANK_CHOICES)
    bank_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    npwp = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User


    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.gender = self.cleaned_data['gender']
        user.phone_number = self.cleaned_data['phone_number']
        user.birth_date = self.cleaned_data['birth_date']
        user.address = self.cleaned_data['address']
        user.bank = self.cleaned_data['bank']
        user.bank_number = self.cleaned_data['bank_number']
        user.npwp = self.cleaned_data['npwp']
        user.image_url = self.cleaned_data['image_url']
        user.is_pekerja = True
        user.save()
        pekerja = Pekerja.objects.create(user=user, gender=self.cleaned_data['gender'], phone_number=self.cleaned_data['phone_number'], address=self.cleaned_data['address'], image_url=self.cleaned_data['image_url'])
        return user