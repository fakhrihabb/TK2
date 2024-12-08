import uuid
from django.db import connection
import psycopg2
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from decimal import Decimal
from django.views.decorators.http import require_POST
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


@login_required
def create_pemesanan(request, subkategori_id, sesi_layanan_id):
    try:
        sesi_layanan = get_sesi_layanan(sesi_layanan_id)
        if not sesi_layanan:
            return HttpResponseForbidden("Sesi layanan tidak ditemukan.")

        harga = sesi_layanan[1]
        subkategori_id = sesi_layanan[2]  # Ambil subkategori_id dari sesi layanan

        if request.method == 'POST':
            # Ambil tanggal dari form, jika kosong gunakan tanggal hari ini
            tanggal_pemesanan = request.POST.get('tanggal_pemesanan')
            if not tanggal_pemesanan:
                tanggal_pemesanan = datetime.now().date()
            else:
                try:
                    tanggal_pemesanan = datetime.strptime(tanggal_pemesanan, "%Y-%m-%d").date()
                except ValueError:
                    return HttpResponseForbidden("Format tanggal tidak valid.")

            diskon = request.POST.get('diskon', None)
            metode_pembayaran = request.POST.get('metode_pembayaran')

            if not metode_pembayaran:
                return HttpResponseForbidden("Data pemesanan tidak lengkap.")

            total_pembayaran = harga
            if diskon == "DISKON10":
                total_pembayaran *= Decimal("0.9")

            # Koneksi ke database
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            cursor = conn.cursor()

            try:
                # Insert ke tabel pemesanan_jasa_pemesananjasa
                insert_query_pemesanan = """
                INSERT INTO pemesanan_jasa_pemesananjasa (pengguna_id, tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, subkategori_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                cursor.execute(insert_query_pemesanan, (
                    request.user.id, tanggal_pemesanan, diskon, total_pembayaran, metode_pembayaran, subkategori_id
                ))
                pemesanan_id = cursor.fetchone()[0]

                # Insert ke tabel pemesanan_jasa_trpemesananstatus dengan status default
                insert_query_status = """
                INSERT INTO pemesanan_jasa_trpemesananstatus (id_tr_pemesanan_id, id_status_id, tgl_waktu)
                VALUES (%s, %s, %s);
                """
                cursor.execute(insert_query_status, (pemesanan_id, '60b058a8-e823-44e9-a57d-89c2ca13c77a', datetime.now()))

                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error saat menyimpan pemesanan: {e}")
                return HttpResponseForbidden("Terjadi kesalahan saat menyimpan pemesanan.")
            finally:
                cursor.close()
                conn.close()

            return redirect('pemesanan_jasa:view_pemesanan')

        current_date = datetime.now().strftime("%Y-%m-%d")
        return render(request, 'create_pemesanan.html', {
            'harga_dasar': harga,
            'sesi_layanan_id': sesi_layanan_id,
            'current_date': current_date
        })
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan.")


def view_pemesanan(request):
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        # Query untuk memperbaiki data subkategori_id yang kosong
        update_query = """
        UPDATE pemesanan_jasa_pemesananjasa
        SET subkategori_id = (SELECT id FROM subkategori_layanan_subkategori LIMIT 1)
        WHERE subkategori_id IS NULL;
        """
        cursor.execute(update_query)

        # Query untuk mengambil daftar subkategori jasa
        query_subkategori = """
        SELECT id, nama FROM subkategori_layanan_subkategori;
        """
        cursor.execute(query_subkategori)
        daftar_subkategori = cursor.fetchall()

        # Query untuk mengambil daftar pesanan beserta statusnya
        query_pesanan = """
        SELECT 
            pj.id, pj.tanggal_pemesanan, pj.diskon, pj.total_pembayaran, pj.metode_pembayaran, 
            pj.pengguna_id, ps.status, COALESCE(sk.nama, 'Subkategori tidak ditemukan') AS nama_subkategori
        FROM pemesanan_jasa_pemesananjasa pj
        LEFT JOIN pemesanan_jasa_trpemesananstatus ts ON pj.id = ts.id_tr_pemesanan_id
        LEFT JOIN pemesanan_jasa_statuspesanan ps ON ts.id_status_id = ps.id
        LEFT JOIN subkategori_layanan_subkategori sk ON pj.subkategori_id = sk.id
        WHERE pj.pengguna_id = %s;
        """
        cursor.execute(query_pesanan, (request.user.id,))
        daftar_pesanan = cursor.fetchall()

        print(f"Debug: Hasil query untuk pengguna_id={request.user.id}: {daftar_pesanan}")

        # Proses hasil query
        pemesanan_dengan_status = []
        for pesanan in daftar_pesanan:
            pemesanan_dengan_status.append({
                'id': pesanan[0],
                'tanggal_pemesanan': pesanan[1],
                'diskon': pesanan[2],
                'total_pembayaran': pesanan[3],
                'metode_pembayaran': pesanan[4],
                'pengguna_id': pesanan[5],
                'status': pesanan[6] or "Status tidak ditemukan",
                'nama_subkategori': pesanan[7] or "Subkategori tidak ditemukan"
            })

        cursor.close()
        conn.close()

        context = {
            'pemesanan_dengan_status': pemesanan_dengan_status,
            'daftar_subkategori': daftar_subkategori
        }
        return render(request, 'view_pemesanan.html', context)

    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan.")

def delete_pemesanan(request, pk):
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        cursor = conn.cursor()

        # Hapus data terkait di tabel pemesanan_jasa_trpemesananstatus
        delete_related_query = """
        DELETE FROM pemesanan_jasa_trpemesananstatus WHERE id_tr_pemesanan_id = %s;
        """
        cursor.execute(delete_related_query, (pk,))
        print(f"Debug: Data terkait untuk pesanan ID {pk} berhasil dihapus dari tabel pemesanan_jasa_trpemesananstatus.")

        # Hapus data di tabel pemesanan_jasa_pemesananjasa
        delete_query = """
        DELETE FROM pemesanan_jasa_pemesananjasa WHERE id = %s;
        """
        cursor.execute(delete_query, (pk,))
        print(f"Debug: Pesanan dengan ID {pk} berhasil dihapus dari tabel pemesanan_jasa_pemesananjasa.")

        conn.commit()

        cursor.close()
        conn.close()

        return redirect('pemesanan_jasa:view_pemesanan')
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponseForbidden("Terjadi kesalahan.")

@csrf_exempt
@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        # Retrieve values from POST request
        testimonial_text = request.POST.get('text')
        rating = request.POST.get('rating')
        id_tr_pemesanan = str(uuid.uuid4())

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