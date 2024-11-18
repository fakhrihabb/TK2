from django import forms

class PembelianVoucherForm(forms.Form):
    voucher_id = forms.IntegerField(widget=forms.HiddenInput())
