import psycopg2
from django.conf import settings
from django.shortcuts import render, redirect
import logging
logger = logging.getLogger(__name__)

from authentication.views import get_user, login, login_required


# Fungsi untuk mendapatkan koneksi database PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )

@login_required
def homepage(request):
    print(request.session.get('phone_number'))
    print(request.session.get('is_pekerja'))
    logger.info("Homepage function called")
    print("Kepanggil nih homepage")
    # Koneksi manual ke database menggunakan psycopg2
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres.cvcodnolmjlcawbfcebn',
        password='KYX-6ri@DN8Q.wc',
        host='aws-0-us-east-1.pooler.supabase.com',
        port='5432',
    )
    cursor = conn.cursor()

    # Query kategori
    cursor.execute("SELECT id, nama_kategori FROM kategori_jasa")
    kategori_list = cursor.fetchall()

    # Query subkategori
    cursor.execute("""
        SELECT s.id, s.nama, s.kategori_id, s.tipe
        FROM subkategori_layanan_subkategori s
    """)
    subkategori_list = cursor.fetchall()

    # Tutup koneksi database
    # cursor.close()
    # conn.close()
    # return render(request, 'error_page.html', {'message': 'Error saat menjalankan query.'})

    # Tentukan role pengguna berdasarkan is_pengguna dan is_pekerja
    is_pengguna = request.session['is_pekerja'] == False
    is_pekerja = request.session['is_pekerja'] == True

    # Debugging role
    # print(f"User: {request.user}, Is Pengguna: {is_pengguna}, Is Pekerja: {is_pekerja}")
    # print(f"User: {request.user}, Is Pengguna: {getattr(request.user, 'is_pengguna', False)}, Is Pekerja: {getattr(request.user, 'is_pekerja', False)}")

    user = get_user(request)
    cursor.close()
    # Render data ke template
    return render(request, 'homepage.html', {
        'kategori_list': kategori_list,
        'subkategori_list': subkategori_list,
        'is_pengguna': is_pengguna,
        'is_pekerja': is_pekerja,
        'user': user,
    })

def not_logged_in(request):
    context = {
        'status': 'not-logged-in'
    }
    return render(request, 'not_logged_in.html', context)
