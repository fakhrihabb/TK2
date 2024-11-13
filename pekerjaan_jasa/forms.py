from django import forms
from .models import ServiceOrder, ServiceSubcategory

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['subcategory', 'customer_name', 'order_date', 'work_date', 'total_cost', 'status']

    subcategory = forms.ModelChoiceField(queryset=ServiceSubcategory.objects.all(), empty_label="Pilih Subkategori")
