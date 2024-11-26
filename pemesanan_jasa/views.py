import psycopg2
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Fungsi untuk query SesiLayanan menggunakan psycopg2
def get_sesi_layanan(subkategori_id):
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )

    cursor = conn.cursor()

    query = """
    SELECT * FROM subkategori_layanan_sesilayanan 
    WHERE subkategori_id = %s
    """
    cursor.execute(query, (subkategori_id,))
    sesi_layanan = cursor.fetchall()

    cursor.close()
    conn.close()

    return sesi_layanan

@login_required
def create_pemesanan(request, sesi_layanan_id):
    sesi_layanan = get_sesi_layanan(sesi_layanan_id)
    if not sesi_layanan:
        return HttpResponseForbidden("Sesi layanan tidak ditemukan.")
    
    harga = sesi_layanan[0][2]  # Misalnya harga ada di kolom ke-3 pada query result

    if request.method == 'POST':
        tanggal_pemesanan = request.POST['tanggal_pemesanan']
        diskon = request.POST.get('diskon', None)
        metode_pembayaran = request.POST['metode_pembayaran']
        
        total_pembayaran = harga
        if diskon == "DISKON10":
            total_pembayaran *= 0.9

        # Menyimpan pemesanan menggunakan psycopg2 (manual query tanpa ORM)
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        # Kolom testimoni_dibuat bertipe datetime, menyimpan waktu saat pemesanan dibuat
        testimoni_dibuat = datetime.now()

        # Query untuk menyimpan pemesanan
        insert_query = """
        INSERT INTO pemesanan_jasa_pemesananjasa (pengguna_id, tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, testimoni_dibuat)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(insert_query, (request.user.id, tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, testimoni_dibuat))
        pesanan_id = cursor.fetchone()[0]  # Ambil ID pemesanan yang baru saja disimpan
        
        # Menentukan status awal pesanan
        status_query = "SELECT id FROM pemesanan_jasa_statuspesanan WHERE status = %s;"
        cursor.execute(status_query, ('menunggu_pembayaran',))
        status_id = cursor.fetchone()[0]

        # Menyimpan status pemesanan
        status_insert_query = """
        INSERT INTO pemesanan_jasa_trpemesananstatus (id_tr_pemesanan_id, id_status_id)
        VALUES (%s, %s);
        """
        cursor.execute(status_insert_query, (pesanan_id, status_id))
        conn.commit()  # Pastikan commit perubahan di database

        cursor.close()
        conn.close()

        return redirect('pemesanan_jasa:view_pemesanan')

    return render(request, 'create_pemesanan.html', {'harga_dasar': harga, 'sesi_layanan_id': sesi_layanan_id})

def view_pemesanan(request):
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    cursor = conn.cursor()

    query = """
    SELECT * FROM pemesanan_jasa_pemesananjasa WHERE pengguna_id = %s;
    """
    cursor.execute(query, (request.user.id,))
    daftar_pesanan = cursor.fetchall()

    # Menambahkan status pemesanan
    pemesanan_status = []
    for pesanan in daftar_pesanan:
        pesanan_id = pesanan[0]  # Misalnya ID pesanan ada di kolom pertama
        status_query = """
        SELECT status FROM pemesanan_jasa_statuspesanan 
        WHERE id = (SELECT id_status_id FROM pemesanan_jasa_trpemesananstatus WHERE id_tr_pemesanan_id = %s);
        """
        cursor.execute(status_query, (pesanan_id,))
        status = cursor.fetchone()[0]
        pemesanan_status.append(status)

    cursor.close()
    conn.close()

    context = {
        'daftar_pesanan': daftar_pesanan,
        'pemesanan_status': pemesanan_status
    }
    return render(request, 'view_pemesanan.html', context)

def delete_pemesanan(request, pk):
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    cursor = conn.cursor()

    # Menghapus pemesanan berdasarkan ID
    delete_query = """
    DELETE FROM pemesanan_jasa_pemesananjasa WHERE id = %s;
    """
    cursor.execute(delete_query, (pk,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('pemesanan_jasa:view_pemesanan')
