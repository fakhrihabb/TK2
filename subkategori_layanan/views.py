from django.shortcuts import redirect, render
from django.db import connection
from django.http import HttpResponseBadRequest
from authentication.views import login_required, get_user

def homepage(request):
    return render(request, 'homepage.html')

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows

@login_required
def subkategori_pengguna(request, subkategori_id):
    try:
        # Ambil data subkategori
        query_subkategori = """
            SELECT id, nama, deskripsi, kategori_id
            FROM subkategori_layanan_subkategori
            WHERE id = %s
        """
        subkategori = execute_query(query_subkategori, [subkategori_id])
        if not subkategori:
            return HttpResponseBadRequest("Subkategori tidak ditemukan.")
        subkategori = subkategori[0]

        # Ambil sesi layanan
        query_sesi_layanan = """
            SELECT id, sesi, harga
            FROM subkategori_layanan_sesilayanan
            WHERE subkategori_id = %s AND tipe_layanan = 'pengguna'
        """
        sesi_layanan = execute_query(query_sesi_layanan, [subkategori_id])

        # Ambil daftar pekerja
        query_pekerja = """
            SELECT 
                sp.pekerja_id,
                CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap,
                pp.nama_bank AS nama_bank,
                pp.nomor_rekening,
                pp.link_foto AS foto,
                pp.rating,
                pp.jml_pesanan_selesai,
                sl.sesi,
                sl.harga
            FROM subkategori_pekerja sp
            INNER JOIN profil_pekerja pp ON sp.pekerja_id = pp.id
            INNER JOIN "USER" u ON pp.user_id = u.id
            INNER JOIN subkategori_layanan_sesilayanan sl 
                ON sp.subkategori_id = sl.subkategori_id
            WHERE sp.subkategori_id = %s AND sl.tipe_layanan = 'pekerja';
        """
        pekerja_list = execute_query(query_pekerja, [subkategori_id])

        query_testimoni = """
        SELECT 
            CONCAT(u_pelanggan.first_name, ' ', u_pelanggan.last_name) AS nama_pelanggan,
            t.Teks AS Testimoni, 
            t.Rating AS Rating, 
            t.Tgl AS TanggalTestimoni,
            CONCAT(u_pekerja.first_name, ' ', u_pekerja.last_name) AS nama_pekerja
        FROM 
            Testimoni t
        LEFT JOIN 
            PEMESANAN_JASA_PEMESANANJASA tpj ON t.IdTrPemesanan = tpj.Id
        LEFT JOIN 
            "USER" u_pelanggan ON tpj.idpengguna = u_pelanggan.Id
        LEFT JOIN 
            "PEKERJA" p_pekerja ON tpj.idpekerja = p_pekerja.user_id
        LEFT JOIN 
            "USER" u_pekerja ON p_pekerja.user_id = u_pekerja.id
        ORDER BY 
            t.Tgl DESC;        
        """
        testimonis = execute_query(query_testimoni)

        query_testimoni = """
        SELECT 
            CONCAT(u_pelanggan.first_name, ' ', u_pelanggan.last_name) AS nama_pelanggan,
            t.Teks AS Testimoni, 
            t.Rating AS Rating, 
            t.Tgl AS TanggalTestimoni,
            CONCAT(u_pekerja.first_name, ' ', u_pekerja.last_name) AS nama_pekerja
        FROM 
            Testimoni t
        LEFT JOIN 
            PEMESANAN_JASA_PEMESANANJASA tpj ON t.IdTrPemesanan = tpj.Id
        LEFT JOIN 
            "USER" u_pelanggan ON tpj.idpengguna = u_pelanggan.Id
        LEFT JOIN 
            "PEKERJA" p_pekerja ON tpj.idpekerja = p_pekerja.user_id
        LEFT JOIN 
            "USER" u_pekerja ON p_pekerja.user_id = u_pekerja.id
        ORDER BY 
            t.Tgl DESC;        
        """
        testimonis = execute_query(query_testimoni)

        user = get_user(request)
        context = {
            'subkategori': subkategori,
            'sesi_layanan': sesi_layanan,
            'pekerja_list': pekerja_list,
            'testimonis': testimonis,  
            'user':user,
        }

        return render(request, 'subkategori_pengguna.html', context)
    except Exception as e:
        return HttpResponseBadRequest(f"Terjadi kesalahan: {e}")

@login_required
def subkategori_pekerja(request, subkategori_id):
    user = get_user(request)

    try:
        # Ambil data subkategori
        query_subkategori = """
            SELECT id, nama, deskripsi, kategori_id
            FROM subkategori_layanan_subkategori
            WHERE id = %s
        """
        subkategori = execute_query(query_subkategori, [subkategori_id])
        if not subkategori:
            return HttpResponseBadRequest("Subkategori tidak ditemukan.")
        subkategori = subkategori[0]

        # Ambil data sesi layanan terkait subkategori
        query_sesi_layanan = """
            SELECT id, sesi, harga
            FROM subkategori_layanan_sesilayanan
            WHERE subkategori_id = %s AND tipe_layanan = 'pekerja'
        """
        sesi_layanan_list = execute_query(query_sesi_layanan, [subkategori_id])

        # Ambil daftar pekerja untuk subkategori
        query_pekerja = """
            SELECT 
                sp.pekerja_id,
                CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap,
                pp.nama_bank AS nama_bank,
                pp.nomor_rekening,
                pp.link_foto AS foto,
                pp.rating,
                pp.jml_pesanan_selesai,
                sl.sesi,
                sl.harga
            FROM subkategori_pekerja sp
            INNER JOIN profil_pekerja pp ON sp.pekerja_id = pp.id
            INNER JOIN "USER" u ON pp.user_id = u.id
            INNER JOIN subkategori_layanan_sesilayanan sl 
                ON sp.subkategori_id = sl.subkategori_id
            WHERE sp.subkategori_id = %s AND sl.tipe_layanan = 'pekerja';
        """
        pekerja_list = execute_query(query_pekerja, [subkategori_id])

        # Validasi apakah pekerja sudah bergabung
        query_is_joined = """
            SELECT 1
            FROM subkategori_pekerja
            WHERE pekerja_id = %s AND subkategori_id = %s
        """
        pekerja_id_result = execute_query(query_is_joined, [user.get("id"), subkategori_id])
        show_join_button = not bool(pekerja_id_result)

        # Jika POST request untuk bergabung
        if request.method == 'POST' and show_join_button:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO subkategori_pekerja (pekerja_id, subkategori_id)
                        VALUES (%s, %s)
                    """, [user.get("id"), subkategori_id])
                # Redirect untuk memperbarui halaman
                return redirect('subkategori_pekerja', subkategori_id=subkategori_id)
            except Exception as e:
                return HttpResponseBadRequest(f"Terjadi kesalahan saat bergabung: {e}")

        context = {
            'subkategori': subkategori,
            'pekerja_list': pekerja_list,
            'sesi_layanan_list': sesi_layanan_list,
            'show_join_button': show_join_button,
            'user': user,
        }
        return render(request, 'subkategori_pekerja.html', context)
    except Exception as e:
        return HttpResponseBadRequest(f"Terjadi kesalahan: {e}")

@login_required
def profil_pekerja(request, pekerja_id):
    try:
        # Ambil profil pekerja
        pekerja_query = """
            SELECT 
                p.id AS pekerja_id, 
                CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap, 
                p.nama_bank, 
                p.nomor_rekening, 
                p.npwp, 
                p.link_foto AS foto, 
                p.rating, 
                p.jml_pesanan_selesai
            FROM profil_pekerja p
            INNER JOIN "USER" u ON p.user_id = u.id
            WHERE p.id = %s
        """
        pekerja = execute_query(pekerja_query, [pekerja_id])
        if not pekerja:
            return HttpResponseBadRequest("Profil pekerja tidak ditemukan.")
        pekerja = pekerja[0]

        context = {
            'pekerja': pekerja
        }
        return render(request, 'profil_pekerja.html', context)
    except Exception as e:
        return HttpResponseBadRequest(f"Terjadi kesalahan: {e}")

def not_logged_in(request):
    if request.session.get('phone_number') != 'not found':
        return redirect('homepage')
    return render(request, 'not_logged_in.html')
