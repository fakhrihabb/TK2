# discounts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import connection
from datetime import datetime, timedelta
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def execute_query(query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                return []
            result = [dict(zip(columns, row)) for row in rows]
            return result
    except Exception as e:
        print(f"Terjadi kesalahan saat menjalankan query: {e}")
        return []  


@login_required
def diskon_list(request):
    if not request.user.is_pengguna:
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    
    try:
        # Query untuk mengambil saldo pengguna
        query_saldo = """
        SELECT saldo 
        FROM authentication_user
        WHERE id = %s;
        """
        saldo_result = execute_query(query_saldo, [request.user.id])
        
        saldo = saldo_result[0]['saldo'] if saldo_result else 0

        # Query untuk mengambil daftar vouchers
        query_vouchers = """
        SELECT 
            V.Kode,
            D.Potongan,
            D.MinTrPemesanan,
            V.JmlHariBerlaku,
            V.KuotaPenggunaan,
            V.Harga
        FROM VOUCHER V
        JOIN DISKON D ON V.Kode = D.Kode
        WHERE V.KuotaPenggunaan > 0;
        """
        vouchers = execute_query(query_vouchers)

        # Query untuk mengambil daftar promos
        query_promos = """
        SELECT Kode, TglAkhirBerlaku
        FROM PROMO 
        WHERE TglAkhirBerlaku > CURRENT_DATE;
        """
        promos = execute_query(query_promos)
        
        context = {
            'saldo': saldo,
            'vouchers': vouchers,
            'promos': promos,
        }
        
        return render(request, 'discounts/diskon_page.html', context)
    
    except Exception as e:
        return HttpResponseForbidden(f"Terjadi kesalahan: {e}")

# Perbaikan pada bagian beli_voucher
def beli_voucher(user_id, voucher_code, payment_method, price, validity, balance):
    try:
        # Pengecekan saldo jika pembayaran menggunakan MyPay
        if payment_method == 'MyPay':
            if balance < price:
                return "Maaf, saldo Anda tidak cukup untuk membeli voucher ini."

            # Kurangi saldo pengguna
            new_balance = balance - price
            query_update_saldo = "UPDATE authentication_user SET saldo = %s WHERE id = %s;"
            execute_query(query_update_saldo, [new_balance, user_id])
        
        # Ambil UUID metode pembayaran
        query_get_method_uuid = "SELECT id FROM METODE_BAYAR WHERE nama = %s;"
        method_result = execute_query(query_get_method_uuid, [payment_method])

        if not method_result or method_result[0] is None:
            return "Metode pembayaran tidak ditemukan atau tidak valid."

        method_uuid = method_result[0]['id']
        pembelian_id = str(uuid.uuid4())

        # Simpan data ke tabel TR_PEMBELIAN_VOUCHER
        validity_days = int(validity)
        tgl_awal = datetime.now().date()
        tgl_akhir = tgl_awal + timedelta(days=validity_days)

        query_insert = """
            INSERT INTO TR_PEMBELIAN_VOUCHER (Id, IdPelanggan, IdVoucher, IdMetodeBayar, TglAwal, TglAkhir, TelahDigunakan)
            VALUES (%s, %s, %s, %s, %s, %s, 0);
        """
        execute_query(query_insert, [pembelian_id, user_id, voucher_code, method_uuid, tgl_awal, tgl_akhir])

        # Ambil kuota voucher
        query_get_kuota = "SELECT KuotaPenggunaan FROM VOUCHER WHERE Kode = %s;"
        kuota_result = execute_query(query_get_kuota, [voucher_code])

        if not kuota_result or kuota_result[0] is None:
            return "Voucher tidak ditemukan."

        kuota = kuota_result[0]['kuotapenggunaan']

        return f"Selamat! Anda berhasil membeli voucher kode {voucher_code}. Voucher ini akan berlaku hingga tanggal {tgl_akhir.strftime('%d/%m/%Y')} dengan kuota penggunaan {kuota} kali."
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

@csrf_exempt
@login_required
def beli_voucher_view(request):
    if request.method == 'POST':
        voucher_code = request.POST.get('voucher_code')
        payment_method = request.POST.get('payment_method')
        voucher_price = int(request.POST.get('voucher_price'))
        voucher_validity = request.POST.get('voucher_validity')

        # Ambil saldo pengguna
        query_saldo = "SELECT saldo FROM authentication_user WHERE id = %s;"
        saldo_result = execute_query(query_saldo, [request.user.id])
        saldo = saldo_result[0]['saldo'] if saldo_result else 0

        # Panggil fungsi beli_voucher
        result_message = beli_voucher(request.user.id, voucher_code, payment_method, voucher_price, voucher_validity, saldo)

        # Return the result to the front end
        if "berhasil" in result_message:
            return JsonResponse({'status': 'success', 'message': result_message})
        else:
            return JsonResponse({'status': 'error', 'message': result_message})
    return JsonResponse({'status': 'error', 'message': 'Request tidak valid.'})


