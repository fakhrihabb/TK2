# discounts/views.py
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.db import connection
from datetime import datetime, timedelta
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from authentication.views import login_required, get_user


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
    user = get_user(request)

    if request.session.get('is_pekerja'):
        return HttpResponseForbidden("Anda tidak memiliki akses ke halaman ini.")
    
    try:
        # Query untuk mengambil saldo pengguna
        query_saldo = """
        SELECT saldo
        FROM "USER"
        WHERE id = %s;
        """
        cursor = connection.cursor()
        cursor.execute(query_saldo, [user['id']])
        result = cursor.fetchone()
        saldo = result[0]
        print(saldo)
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
        user = get_user(request)
        context = {
            'saldo': saldo,
            'vouchers': vouchers,
            'promos': promos, 'user': user,
        }
        cursor.close()
        return render(request, 'discounts/diskon_page.html', context)
    
    except Exception as e:
        return HttpResponseForbidden(f"Terjadi kesalahan: {e}")

# Perbaikan pada bagian beli_voucher
def beli_voucher(user_id, voucher_code, payment_method, price, validity, balance):
    try:
        cursor = connection.cursor()
        # Pengecekan saldo jika pembayaran menggunakan MyPay
        if payment_method == 'MyPay':
            if balance < price:
                return "Maaf, saldo Anda tidak cukup untuk membeli voucher ini."

            # Kurangi saldo pengguna
            new_balance = balance - price

            cursor.execute("""
            UPDATE "USER"
            SET saldo = %s
            WHERE id = %s;
            """, [new_balance, user_id])
            # query_update_saldo = 'UPDATE "USER" SET saldo = %s WHERE id = %s;'
            # execute_query(query_update_saldo, [new_balance, user_id])

        # Ambil UUID metode pembayaran
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM METODE_BAYAR WHERE nama = %s;", [payment_method])
        result = cursor.fetchone()

        if not result or result[0] is None:
            return "Metode pembayaran tidak ditemukan atau tidak valid."

        method_uuid = result[0]
        pembelian_id = str(uuid.uuid4())

        # Simpan data ke tabel TR_PEMBELIAN_VOUCHER
        validity_days = int(validity)
        tgl_awal = datetime.now().date()
        tgl_akhir = tgl_awal + timedelta(days=validity_days)

        query_insert = """
            INSERT INTO TR_PEMBELIAN_VOUCHER (Id, IdPelanggan, IdVoucher, IdMetodeBayar, TglAwal, TglAkhir, TelahDigunakan)
            VALUES (%s, %s, %s, %s, %s, %s, 0);
        """
        cursor.execute(query_insert, [pembelian_id, user_id, voucher_code, method_uuid, tgl_awal, tgl_akhir])

        # Ambil kuota voucher
        query_get_kuota = "SELECT KuotaPenggunaan FROM VOUCHER WHERE Kode = %s;"
        kuota_result = execute_query(query_get_kuota, [voucher_code])

        if not kuota_result or kuota_result[0] is None:
            return "Voucher tidak ditemukan."

        kuota = kuota_result[0]['kuotapenggunaan']
        cursor.close()
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
        user = get_user(request)
        # Ambil saldo pengguna
        cursor = connection.cursor()
        query_saldo = 'SELECT saldo FROM "USER" WHERE id = %s;'
        saldo_result = cursor.execute(query_saldo, [user['id']])
        result = cursor.fetchone()
        saldo = result[0]

        # Panggil fungsi beli_voucher
        result_message = beli_voucher(user['id'], voucher_code, payment_method, voucher_price, voucher_validity, saldo)

        cursor.close()

        # Return the result to the front end
        if "berhasil" in result_message:
            return JsonResponse({'status': 'success', 'message': result_message})
        else:
            return JsonResponse({'status': 'error', 'message': result_message})
    return JsonResponse({'status': 'error', 'message': 'Request tidak valid.'})


