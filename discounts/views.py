import json
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PembelianVoucherForm

def load_dummy_data():
    file_path = os.path.join(settings.BASE_DIR, 'discounts/fixtures/dummy_discounts.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def diskon_list(request):
    data = load_dummy_data()  
    vouchers = data['vouchers']
    promos = data['promos']
    
    context = {
        'vouchers': vouchers,
        'promos': promos,
        'pembelian_form': PembelianVoucherForm()
    }
    return render(request, 'discounts/diskon_page.html', context)

def beli_voucher(request):
    if request.method == 'POST':
        form = PembelianVoucherForm(request.POST)
        if form.is_valid():
            data = load_dummy_data()
            vouchers = data['vouchers']
            
            voucher_id = form.cleaned_data['voucher_id']
            voucher_data = next((v for v in vouchers if v['id'] == voucher_id), None)

            user_profile = request.user.profile  

            if voucher_data and user_profile.saldo >= voucher_data['harga']:
                user_profile.saldo -= voucher_data['harga']
                user_profile.save()

                messages.success(
                    request,
                    f"Selamat! Anda berhasil membeli voucher {voucher_data['kode']}. "
                    f"Voucher ini berlaku hingga {voucher_data['masa_berlaku']} dengan kuota penggunaan sebanyak {voucher_data['kuota_penggunaan']} kali."
                )
            else:
                messages.error(request, "Maaf, saldo Anda tidak cukup untuk membeli voucher ini.")
                
    return redirect('diskon-page')
