from django.shortcuts import render, get_object_or_404
from .models import Subkategori, SesiLayanan, Pekerja, Testimoni

def homepage(request):
    return render(request, 'homepage.html')

def subkategori_detail(request, subkategori_id):
    subkategori = get_object_or_404(Subkategori, id=subkategori_id)
    sesi_layanan = SesiLayanan.objects.filter(subkategori=subkategori)
    pekerja_list = Pekerja.objects.filter(subkategori=subkategori)
    testimoni_list = Testimoni.objects.filter(subkategori=subkategori)

    context = {
        'subkategori': subkategori,
        'sesi_layanan': sesi_layanan,
        'pekerja_list': pekerja_list,
        'testimoni_list': testimoni_list,
    }
    return render(request, 'subkategori_pengguna.html', context)

def subkategori_pengguna(request, subkategori_id):
    subkategori = get_object_or_404(Subkategori, id=subkategori_id)
    sesi_layanan = SesiLayanan.objects.filter(subkategori=subkategori)
    testimoni_list = Testimoni.objects.filter(subkategori=subkategori)

    context = {
        'subkategori': subkategori,
        'sesi_layanan': sesi_layanan,
        'testimoni_list': testimoni_list,
    }
    return render(request, 'subkategori_pengguna.html', context)

def subkategori_pekerja(request, subkategori_id):
    # Ambil subkategori berdasarkan ID dan pastikan tipe pekerja
    subkategori = get_object_or_404(Subkategori, id=subkategori_id, tipe='pekerja')
    
    context = {
        'subkategori': subkategori
    }
    return render(request, 'subkategori_pekerja.html', context)

def create_pemesanan(request):
    if request.method == 'POST':
        # Logika untuk menyimpan pemesanan
        pass

    return render(request, 'pemesanan_jasa/create_pemesanan.html')

def profil_pekerja(request, nama_pekerja):
    # Data statis untuk profil pekerja
    data_pekerja = {
        "Pekerja 1": {"nama": "Pekerja 1", "rating": 4.5, "deskripsi": "Profesional dalam kebersihan rumah"},
        "Pekerja 2": {"nama": "Pekerja 2", "rating": 4.2, "deskripsi": "Ahli dalam kebersihan apartemen"},
        "Pekerja 3": {"nama": "Pekerja 3", "rating": 4.8, "deskripsi": "Berpengalaman dalam pembersihan kantor"},
    }

    # Ambil data berdasarkan nama pekerja
    pekerja = data_pekerja.get(nama_pekerja, {"nama": "Tidak Ditemukan", "rating": 0, "deskripsi": "Profil tidak tersedia"})

    context = {
        'pekerja': pekerja
    }
    return render(request, 'profil_pekerja.html', context)
