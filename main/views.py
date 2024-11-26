import psycopg2
from django.conf import settings
from django.shortcuts import render

# Fungsi untuk mendapatkan koneksi database PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )

def homepage(request):
    # Koneksi ke database
    conn = get_db_connection()
    cur = conn.cursor()

    # Menulis query SQL untuk mengambil semua subkategori
    cur.execute("SELECT * FROM subkategori_layanan_subkategori;")
    
    # Ambil hasil query
    subkategori_list = cur.fetchall()

    # Menutup koneksi
    cur.close()
    conn.close()

    # Mengirim data ke template
    return render(request, 'homepage.html', {'subkategori_list': subkategori_list})

def not_logged_in(request):
    context = {
        'status': 'not-logged-in'
    }
    return render(request, 'not_logged_in.html', context)
