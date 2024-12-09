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

        # Ambil daftar pekerja (casting bigint ke uuid)
        query_pekerja = """
    SELECT 
        p.user_id,
        CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap,
        p.bank, p.bank_number, p.image_url, p.rating, p.order_complete
    FROM subkategori_pekerja sp
    INNER JOIN public."PEKERJA" p ON sp.pekerja_id = p.user_id
    INNER JOIN "USER" u ON p.user_id = u.id
    WHERE sp.subkategori_id = %s;
"""

        pekerja_list = execute_query(query_pekerja, [subkategori_id])

        user = get_user(request)
        context = {
            'subkategori': subkategori,
            'sesi_layanan': sesi_layanan,
            'pekerja_list': pekerja_list,
            'testimonis': [],  # Dummy data untuk testimoni
            'user': user,
        }

        return render(request, 'subkategori_pengguna.html', context)
    except Exception as e:
        return HttpResponseBadRequest(f"Terjadi kesalahan: {e}")


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
        print("Subkategori ID dari request:", subkategori_id)

        # Ambil data sesi layanan terkait subkategori
        query_sesi_layanan = """
            SELECT id, sesi, harga
            FROM subkategori_layanan_sesilayanan
            WHERE subkategori_id = %s AND tipe_layanan = 'pekerja'
        """
        sesi_layanan_list = execute_query(query_sesi_layanan, [subkategori_id])
        print("Hasil Query Sesi Layanan:", sesi_layanan_list)

        # Ambil pekerja yang tergabung
        query_pekerja = """
    SELECT 
        p.user_id,
        CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap,
        p.bank, p.bank_number, p.image_url, p.rating, p.order_complete
    FROM subkategori_pekerja sp
    INNER JOIN public."PEKERJA" p ON sp.pekerja_id = p.user_id
    INNER JOIN "USER" u ON p.user_id = u.id
    WHERE sp.subkategori_id = %s;
"""

        pekerja_list = execute_query(query_pekerja, [subkategori_id])

        # Validasi user login
        # Validasi user login
        if not request.user.is_authenticated:
            return redirect('not_logged_in')

        # Ambil ID pekerja dari user yang login
        query_user_pekerja = """
            SELECT id
            FROM profil_pekerja
            WHERE user_id = %s
        """
        pekerja_id_result = execute_query(query_user_pekerja, [user.get("id")])
        if not pekerja_id_result:
            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO profil_pekerja (
                        id, nama, nama_bank, nomor_rekening, npwp, link_foto, rating, jml_pesanan_selesai, user_id
                    ) VALUES (
                        gen_random_uuid(), 
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                cursor.execute(insert_query, [
                    f"{user.get("first_name")} {request.user.last_name}",  # Gabungan nama depan dan belakang
                    'Bank Default',  # Bank default
                    '0000000000',  # Nomor rekening default
                    'NPWP-DEFAULT',  # NPWP default
                    'https://example.com/default-profile.jpg',  # Foto default
                    0.0,  # Rating default
                    0,  # Jumlah pesanan selesai default
                    request.user.id  # ID user
                ])

            pekerja_id_result = execute_query(query_user_pekerja, [request.user.id])

        user_pekerja_id = pekerja_id_result[0]['id']

        # Tentukan apakah pekerja sudah bergabung
        query_is_joined = """
            SELECT 1
            FROM subkategori_pekerja
            WHERE pekerja_id = %s AND subkategori_id = %s
        """
        is_joined_result = execute_query(query_is_joined, [user_pekerja_id, subkategori_id])
        show_join_button = not bool(is_joined_result)

        # Jika POST untuk bergabung
        if request.method == 'POST' and show_join_button:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO subkategori_pekerja (pekerja_id, subkategori_id)
                    VALUES (%s, %s)
                """, [user_pekerja_id, subkategori_id])
            return redirect('subkategori_pekerja', subkategori_id=subkategori_id)

        user = get_user(request)
        print("User dari request:", request.user)
        print("User dari get_user:", get_user(request))

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


def profil_pekerja(request, pekerja_id):
    pekerja = execute_query("""
        SELECT 
            p.id, 
            CONCAT(u.first_name, ' ', u.last_name) AS nama_lengkap, 
            p.nama_bank, 
            p.nomor_rekening, 
            p.npwp, 
            p.link_foto, 
            p.rating, 
            p.jml_pesanan_selesai
        FROM profil_pekerja p
        INNER JOIN "USER"" u ON p.user_id = u.id
        WHERE p.id = %s
    """, [pekerja_id])

    if not pekerja:
        return HttpResponseBadRequest("Profil pekerja tidak ditemukan.")

    return render(request, 'profil_pekerja.html', {'pekerja': pekerja[0]})


def not_logged_in(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    return render(request, 'not_logged_in.html')
