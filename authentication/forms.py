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
    def save(self, commit=True):  # Tambahkan commit=True
        user = super().save(commit=False)  # Save tanpa langsung menyimpan ke database
        user.is_pengguna = True
        if commit:  # Simpan hanya jika commit=True
            user.save()
        Pengguna.objects.create(
            user=user,
            gender=self.cleaned_data['gender'],
            phone_number=self.cleaned_data['phone_number'],
            birth_date=self.cleaned_data['birth_date'],
            address=self.cleaned_data['address']
        )
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
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_pekerja = True
        user.save() if commit else None

        # Pastikan semua field yang diperlukan untuk Pekerja disertakan
        pekerja = Pekerja.objects.create(
            user=user,
            gender=self.cleaned_data['gender'],
            phone_number=self.cleaned_data['phone_number'],
            birth_date=self.cleaned_data['birth_date'],  # Tambahkan field birth_date
            address=self.cleaned_data['address'],
            bank=self.cleaned_data['bank'],
            bank_number=self.cleaned_data['bank_number'],
            npwp=self.cleaned_data['npwp'],
            image_url=self.cleaned_data['image_url']
        )
        return user