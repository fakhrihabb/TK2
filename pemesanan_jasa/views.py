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
from discounts.views import diskon_list, execute_query
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
        # Get sesi layanan details
        sesi_layanan = get_sesi_layanan(sesi_layanan_id)
        if not sesi_layanan:
            return render(request, 'create_pemesanan.html', {
                'error_message': "Sesi layanan tidak ditemukan."
            })

        harga = sesi_layanan[1]
        subkategori_id = sesi_layanan[2]

        # Get user, diskon, dan metode pembayaran
        user = get_user(request)
        if not user:
            return render(request, 'create_pemesanan.html', {
                'error_message': "Silakan login terlebih dahulu."
            })

        diskon_list = get_diskon()
        metode_pembayaran = get_metode_pembayaran()

        # Debug logs
        print("Debug: create_pemesanan dipanggil")
        print(f"Subkategori ID: {subkategori_id}, Sesi Layanan ID: {sesi_layanan_id}")

        if request.method == 'POST':
            # Get form data
            tanggal_pemesanan = request.POST.get('tanggal_pemesanan')
            waktu_pekerjaan = request.POST.get('waktu_pekerjaan')
            diskon_kode = request.POST.get('diskon')
            metode_pembayaran_id = request.POST.get('metode_pembayaran')

            # Validate required fields
            if not waktu_pekerjaan:
                return render(request, 'create_pemesanan.html', {
                    'error_message': "Mohon pilih waktu pekerjaan.",
                    'harga_dasar': harga,
                    'current_date': datetime.now().strftime("%Y-%m-%d"),
                    'metode_pembayaran_list': metode_pembayaran,
                    'diskon_list': diskon_list,
                    'user': user
                })

            if not metode_pembayaran_id:
                return render(request, 'create_pemesanan.html', {
                    'error_message': "Mohon pilih metode pembayaran.",
                    'harga_dasar': harga,
                    'current_date': datetime.now().strftime("%Y-%m-%d"),
                    'metode_pembayaran_list': metode_pembayaran,
                    'diskon_list': diskon_list,
                    'user': user
                })

            try:
                # Check user balance
                cursor = connection.cursor()
                cursor.execute("SELECT saldo FROM \"USER\" WHERE id = %s;", [user['id']])
                saldo = cursor.fetchone()[0]
                print(f"Debug: Saldo pengguna adalah {saldo}")

                # Calculate total payment
                total_pembayaran = harga
                if diskon_kode and diskon_kode.strip():
                    cursor.execute("SELECT potongan FROM diskon WHERE kode = %s;", (diskon_kode,))
                    potongan = cursor.fetchone()
                    if potongan:
                        total_pembayaran -= Decimal(potongan[0])

                # Check if balance is sufficient
                if total_pembayaran > saldo:
                    return render(request, 'create_pemesanan.html', {
                        'error_message': f"Saldo Anda tidak mencukupi. Total pembayaran: Rp {total_pembayaran:,.2f}, Saldo Anda: Rp {saldo:,.2f}",
                        'harga_dasar': harga,
                        'current_date': datetime.now().strftime("%Y-%m-%d"),
                        'metode_pembayaran_list': metode_pembayaran,
                        'diskon_list': diskon_list,
                        'user': user
                    })

                # Begin transaction
                with connection.cursor() as cursor:
                    try:
                        # Disable trigger temporarily
                        cursor.execute(
                            "ALTER TABLE pemesanan_jasa_pemesananjasa DISABLE TRIGGER before_insert_update_tr_pemesanan_jasa;")

                        # Insert pemesanan
                        if diskon_kode and diskon_kode.strip():
                            insert_pemesanan_query = """
                            INSERT INTO pemesanan_jasa_pemesananjasa 
                            (idpengguna, tanggal_pemesanan, waktu_pekerjaan, diskon, total_pembayaran, 
                            metode_pembayaran, subkategori_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                            """
                            values = (user['id'], tanggal_pemesanan, waktu_pekerjaan, diskon_kode,
                                      total_pembayaran, metode_pembayaran_id, subkategori_id)
                        else:
                            insert_pemesanan_query = """
                            INSERT INTO pemesanan_jasa_pemesananjasa 
                            (idpengguna, tanggal_pemesanan, waktu_pekerjaan, total_pembayaran, 
                            metode_pembayaran, subkategori_id)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id;
                            """
                            values = (user['id'], tanggal_pemesanan, waktu_pekerjaan,
                                      total_pembayaran, metode_pembayaran_id, subkategori_id)

                        cursor.execute(insert_pemesanan_query, values)
                        pemesanan_id = cursor.fetchone()[0]

                        # Insert status
                        default_status_id = '60b058a8-e823-44e9-a57d-89c2ca13c77a'
                        cursor.execute("""
                        INSERT INTO pemesanan_jasa_trpemesananstatus 
                        (id_tr_pemesanan_id, id_status_id, tgl_waktu)
                        VALUES (%s, %s, %s);
                        """, (pemesanan_id, default_status_id, datetime.now()))

                        # Update user balance
                        cursor.execute("""
                        UPDATE "USER"
                        SET saldo = saldo - %s
                        WHERE id = %s;
                        """, [total_pembayaran, user['id']])

                        # Re-enable trigger
                        cursor.execute(
                            "ALTER TABLE pemesanan_jasa_pemesananjasa ENABLE TRIGGER before_insert_update_tr_pemesanan_jasa;")

                        # Commit transaction
                        connection.commit()

                        return redirect('pemesanan_jasa:view_pemesanan')

                    except Exception as e:
                        connection.rollback()
                        print(f"Error saat menyimpan pemesanan: {e}")
                        return render(request, 'create_pemesanan.html', {
                            'error_message': "Terjadi kesalahan saat menyimpan pemesanan. Silakan coba lagi.",
                            'harga_dasar': harga,
                            'current_date': datetime.now().strftime("%Y-%m-%d"),
                            'metode_pembayaran_list': metode_pembayaran,
                            'diskon_list': diskon_list,
                            'user': user
                        })

            except Exception as e:
                print(f"Error: {e}")
                return render(request, 'create_pemesanan.html', {
                    'error_message': "Terjadi kesalahan. Silakan coba lagi.",
                    'harga_dasar': harga,
                    'current_date': datetime.now().strftime("%Y-%m-%d"),
                    'metode_pembayaran_list': metode_pembayaran,
                    'diskon_list': diskon_list,
                    'user': user
                })

        # GET request - display form
        current_date = datetime.now().strftime("%Y-%m-%d")
        return render(request, 'create_pemesanan.html', {
            'harga_dasar': harga,
            'current_date': current_date,
            'metode_pembayaran_list': metode_pembayaran,
            'diskon_list': diskon_list,
            'user': user,
        })

    except Exception as e:
        print(f"Error: {e}")
        return render(request, 'create_pemesanan.html', {
            'error_message': "Terjadi kesalahan sistem. Silakan coba lagi nanti."
        })


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
            pj.id, pj.tanggal_pemesanan, pj.waktu_pekerjaan, pj.diskon, pj.total_pembayaran, 
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
                'waktu_pekerjaan': pesanan[2],  # Tambahkan ini
                'diskon': pesanan[3],
                'total_pembayaran': pesanan[4],
                'metode_pembayaran': pesanan[5],
                'idpengguna': pesanan[6],
                'status': pesanan[7],
                'nama_subkategori': pesanan[8],
                'allow_cancellation': allow_cancellation,
            })

        cursor.close()
        conn.close()

        user = get_user(request)
        return render(request, 'view_pemesanan.html',
                      {'pemesanan_dengan_status': pemesanan_dengan_status, 'user': user})
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
        FROM PEMESANAN_JASA_PEMESANANJASA
        WHERE Idpengguna =  %s;
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
    pj.id, pj.tanggal_pemesanan, pj.waktu_pekerjaan, pj.diskon, pj.total_pembayaran, 
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
                'waktu_pekerjaan': pesanan[2],  # Tambahkan ini
                'diskon': pesanan[3],
                'total_pembayaran': pesanan[4],
                'metode_pembayaran': pesanan[5],
                'idpengguna': pesanan[6],
                'status': pesanan[7],
                'nama_subkategori': pesanan[8],
                'allow_cancellation': allow_cancellation,
            })

        cursor.close()
        conn.close()

        user = get_user(request)
        return render(request, 'view_pemesanan.html',
                      {'pemesanan_dengan_status': pemesanan_dengan_status, 'user': user})
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
        FROM PEMESANAN_JASA_PEMESANANJASA
        WHERE Idpengguna =  %s;
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
