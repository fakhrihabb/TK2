from django import forms
from .models import PemesananJasa

class PemesananForm(forms.ModelForm):
    class Meta:
        model = PemesananJasa
        fields = ['tanggal_pemesanan', 'diskon', 'total_pembayaran', 'metode_pembayaran']
