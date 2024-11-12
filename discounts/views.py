# discounts/views.py
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import PembelianVoucherForm
import os
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def load_dummy_data():
    file_path = os.path.join(settings.BASE_DIR, 'discounts/fixtures/dummy_discounts.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


@login_required
def diskon_list(request):
    if not request.user.is_pengguna:
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    
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
                
    return redirect('discounts:diskon_page')  
