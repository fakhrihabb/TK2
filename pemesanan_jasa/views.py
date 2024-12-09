from django.db import connection
import psycopg2
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
import uuid
from django.conf import settings
from authentication.views import get_user
from discounts.views import execute_query
from django.views.decorators.csrf import csrf_exempt

# Fungsi untuk query SesiLayanan menggunakan psycopg2
def get_sesi_layanan(sesi_layanan_id):
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    cursor = conn.cursor()

    query = """
    SELECT id, harga, subkategori_id
    FROM subkategori_layanan_sesilayanan
    WHERE id = %s
    """
    cursor.execute(query, (sesi_layanan_id,))
    sesi_layanan = cursor.fetchone()

    print(f"Debug: sesi_layanan_id={sesi_layanan_id}, hasil={sesi_layanan}")  # Debugging tambahan

    cursor.close()
    conn.close()

    return sesi_layanan

def create_pemesanan(request, subkategori_id, sesi_layanan_id):
    try:
        sesi_layanan = get_sesi_layanan(sesi_layanan_id)
        if not sesi_layanan:
            return HttpResponseForbidden("Sesi layanan tidak ditemukan.")

        harga = sesi_layanan[1]
        subkategori_id = sesi_layanan[2]

        # Ambil data diskon dan metode pembayaran
        diskon_list = get_diskon()
        metode_pembayaran_list = get_metode_pembayaran()

        # Tambahkan log debugging untuk memastikan fungsi dipanggil
        print("Debug: create_pemesanan dipanggil")
        print(f"Subkategori ID: {subkategori_id}, Sesi Layanan ID: {sesi_layanan_id}")

        if request.method == 'POST':
            tanggal_pemesanan = request.POST.get('tanggal_pemesanan')
            diskon = request.POST.get('diskon', None)
            metode_pembayaran = request.POST.get('metode_pembayaran')

            if not metode_pembayaran:
                return HttpResponseForbidden("Metode pembayaran tidak dipilih.")

            try:
                # Ambil user ID dari session
                user = get_user(request)
                if not user:
                    return HttpResponseForbidden("Pengguna tidak ditemukan.")

                # Pastikan saldo pengguna tersedia
                query_saldo = """
                SELECT saldo
                FROM "USER"
                WHERE id = %s;
                """
                cursor = connection.cursor()
                cursor.execute(query_saldo, [user['id']])
                result = cursor.fetchone()
                if result is None:
                    return HttpResponseForbidden("Saldo pengguna tidak ditemukan.")
                saldo = result[0]
                print(f"Debug: Saldo pengguna adalah {saldo}")
            except Exception as e:
                print(f"Error saat mengambil saldo: {e}")
                return HttpResponseForbidden("Terjadi kesalahan saat validasi saldo pengguna.")

            # Hitung total pembayaran dengan diskon
            total_pembayaran = harga
            if diskon:
                with psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT potongan FROM diskon WHERE kode = %s;", (diskon,))
                        potongan = cursor.fetchone()
                        if potongan:
                            total_pembayaran -= Decimal(potongan[0])

            # Simpan data ke database
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    try:
                        # Simpan data ke tabel pemesanan_jasa_pemesananjasa
                        insert_pemesanan_query = """
                        INSERT INTO pemesanan_jasa_pemesananjasa (idpengguna, tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, subkategori_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """
                        cursor.execute(insert_pemesanan_query, (
                            user['id'], tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, subkategori_id
                        ))
                        pemesanan_id = cursor.fetchone()[0]

                        # Tambahkan status default "Menunggu Pembayaran"
                        insert_status_query = """
                        INSERT INTO pemesanan_jasa_trpemesananstatus (id_tr_pemesanan_id, id_status_id, tgl_waktu)
                        VALUES (%s, %s, %s);
                        """
                        default_status_id = '60b058a8-e823-44e9-a57d-89c2ca13c77a'  # UUID status default
                        cursor.execute(insert_status_query, (pemesanan_id, default_status_id, datetime.now()))

                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print(f"Error saat menyimpan pemesanan: {e}")
                        return HttpResponseForbidden("Terjadi kesalahan saat menyimpan pemesanan.")

            return redirect('pemesanan_jasa:view_pemesanan')
        
        user = get_user(request)
        current_date = datetime.now().strftime("%Y-%m-%d")
        return render(request, 'create_pemesanan.html', {
            'harga_dasar': harga,
            'current_date': current_date,
            'metode_pembayaran_list': metode_pembayaran_list,
            'diskon_list': diskon_list,
            'user':user,
        })

    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan.")

def get_metode_pembayaran():
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        query = "SELECT id, nama FROM metode_bayar;"
        cursor.execute(query)
        metode_pembayaran = cursor.fetchall()

        cursor.close()
        conn.close()
        return metode_pembayaran
    except Exception as e:
        print(f"Error saat mengambil metode pembayaran: {e}")
        return []
    
def get_diskon():
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()
        query = "SELECT kode, potongan FROM diskon;"
        cursor.execute(query)
        diskon_list = cursor.fetchall()

        print(f"Debug: diskon_list={diskon_list}")  # Debugging
        cursor.close()
        conn.close()
        return diskon_list
    except Exception as e:
        print(f"Error saat mengambil diskon: {e}")
        return []

def view_pemesanan(request):
    try:
        user = get_user(request)
        if not user:
            return HttpResponseForbidden("Anda harus login untuk mengakses halaman ini.")

        user_id = user['id']

        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        query_pesanan = """
        SELECT DISTINCT 
            pj.id, pj.tanggal_pemesanan, pj.diskon, pj.total_pembayaran, 
            COALESCE(mb.nama, 'Metode tidak ditemukan') AS metode_pembayaran,
            pj.idpengguna, COALESCE(ps.status, 'Menunggu Pembayaran') AS status,
            COALESCE(sk.nama, 'Subkategori tidak ditemukan') AS nama_subkategori
        FROM pemesanan_jasa_pemesananjasa pj
        LEFT JOIN pemesanan_jasa_trpemesananstatus ts ON pj.id = ts.id_tr_pemesanan_id
        LEFT JOIN pemesanan_jasa_statuspesanan ps ON ts.id_status_id = ps.id
        LEFT JOIN subkategori_layanan_subkategori sk ON pj.subkategori_id = sk.id
        LEFT JOIN metode_bayar mb ON pj.metode_pembayaran = mb.id
        WHERE pj.idpengguna = %s;
        """
        cursor.execute(query_pesanan, (str(user_id),))
        daftar_pesanan = cursor.fetchall()

        pemesanan_dengan_status = []
        for pesanan in daftar_pesanan:
            status = pesanan[6]
            allow_cancellation = status in ["Menunggu Pembayaran", "Mencari Pekerja Terdekat"]

            pemesanan_dengan_status.append({
                'id': pesanan[0],
                'tanggal_pemesanan': pesanan[1],
                'diskon': pesanan[2],
                'total_pembayaran': pesanan[3],
                'metode_pembayaran': pesanan[4],
                'idpengguna': pesanan[5],
                'status': status,
                'nama_subkategori': pesanan[7],
                'allow_cancellation': allow_cancellation,  # Tambahkan flag
            })

        cursor.close()
        conn.close()

        user = get_user(request)
        return render(request, 'view_pemesanan.html', {'pemesanan_dengan_status': pemesanan_dengan_status,'user':user})
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan.")

def delete_pemesanan(request, pk):
    try:
        pk = uuid.UUID(str(pk))  # Validasi UUID
    except ValueError:
        return HttpResponseForbidden("ID pesanan tidak valid.")

    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        # Hapus data terkait
        delete_related_query = """
        DELETE FROM pemesanan_jasa_trpemesananstatus WHERE id_tr_pemesanan_id = %s;
        """
        cursor.execute(delete_related_query, (pk,))

        delete_query = """
        DELETE FROM pemesanan_jasa_pemesananjasa WHERE id = %s;
        """
        cursor.execute(delete_query, (pk,))

        conn.commit()

        
        return JsonResponse({"message": "Pesanan berhasil dibatalkan."}, status=200)
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan saat menghapus pesanan.")

@csrf_exempt
def submit_testimonial(request):
    user = get_user(request)
    if request.method == 'POST':
        # Retrieve values from POST request
        testimonial_text = request.POST.get('text')
        rating = request.POST.get('rating')

        query_idtrpemesanan = """
        SELECT Id
        FROM TR_PEMESANAN_JASA
        WHERE IdPelanggan =  %s;
        """
        cursor = connection.cursor()
        cursor.execute(query_idtrpemesanan, [user['id']])
        result = cursor.fetchone()
        id_tr_pemesanan = result[0]

        # Check if required fields are present
        if testimonial_text and rating and id_tr_pemesanan:
            try:
                query_insert = """
                    INSERT INTO Testimoni (IdTrPemesanan, Teks, Rating, tgl)
                    VALUES (%s, %s, %s, NOW());
                """
                execute_query(query_insert, [id_tr_pemesanan, testimonial_text, rating])

                return JsonResponse({'status': 'success'})
            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})