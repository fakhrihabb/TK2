from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.db import connection
from authentication.views import login_required
import psycopg2
from authentication.views import get_user

# Konfigurasi database PostgreSQL
DB_CONFIG = {
    'dbname': 'postgres',   
    'user': 'postgres.cvcodnolmjlcawbfcebn',          
    'password': 'KYX-6ri@DN8Q.wc',    
    'host': 'aws-0-us-east-1.pooler.supabase.com',             
    'port': '5432'                 
}

@login_required
def mypay(request):
    user = get_user(request) 
    if not user['logged_in']:
        return redirect('authentication:login')

    try:
        with connection.cursor() as cursor:
            # Hitung saldo untuk pengguna tertentu
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0.0) 
                FROM mypay_transaction 
                WHERE user_id = %s;
            """, [user['id']])
            balance = cursor.fetchone()[0]

            # Ambil transaksi untuk pengguna tertentu
            cursor.execute("""
                SELECT date, category, amount, description 
                FROM mypay_transaction 
                WHERE user_id = %s 
                ORDER BY date DESC;
            """, [user['id']])
            transactions = cursor.fetchall()
    except Exception as e:
        balance = 0.0
        transactions = []
        print(f"Error: {e}")

    return render(request, 'mypay/mypay.html', {
        'balance': balance,
        'transactions': transactions,
        'user': user,
    })

@login_required
def transaksi(request):
    user = get_user(request)  # Dapatkan data pengguna yang login
    if not user['logged_in']:
        return redirect('authentication:login')

    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')  # Deskripsi bisa kosong

        # Debugging: Periksa apakah data diterima dengan benar
        print(f"Category: {category}, Amount: {amount}, Description: {description}")
        
        # Validasi input untuk kategori dan amount
        if not category or not amount:
            messages.error(request, "Kategori dan jumlah harus diisi.")
            return redirect('mypay:transaksi')

        try:
            # Memasukkan data ke database
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Menyisipkan data transaksi ke tabel berdasarkan kategori
            if category == 'topup':
                amount = request.POST.get('amount')
                description = 'Top Up MyPay'
            elif category == 'jasa':
                amount = 100000  # Harga tetap untuk jasa, atau bisa diambil dinamis sesuai pilihan
                description = request.POST.get('description')
            elif category == 'transfer':
                amount = request.POST.get('amount')
                description = request.POST.get('description')  # Nomor HP tujuan
            elif category == 'withdrawal':
                amount = request.POST.get('amount')
                description = request.POST.get('description')  # Bank tujuan

            # Insert ke database
            cursor.execute("""
                INSERT INTO mypay_transaction (user_id, date, category, amount, description)
                VALUES (%s, CURRENT_DATE, %s, %s, %s);
            """, (user['id'], category, amount, description))

            connection.commit()
            messages.success(request, "Transaksi berhasil!")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {e}")
        finally:
            cursor.close()
            connection.close()

        return redirect('mypay:mypay')

    return render(request, 'mypay/transaksi.html', {'user': user})
