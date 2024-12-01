import psycopg2
from django.conf import settings
from django.shortcuts import render, redirect

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

    # Me-retreive user yang aktif
    user = get_user(request)
    print(user)
    # Mengirim data ke template
    return render(request, 'homepage.html', {'subkategori_list': subkategori_list, 'user': user})

def not_logged_in(request):
    if request.session.get('phone_number', 'not found') != 'not found' or request.session.get('is_pekerja', 'not found') != 'not found' or request.session.get('user_id' ,'not found') != 'not found':
        print(request.session['phone_number'], request.session['is_pekerja'], request.session['user_id'])
        return redirect('homepage')
    else:
        return render(request, 'not_logged_in.html')
