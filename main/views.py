from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from subkategori_layanan.models import Kategori, Subkategori

def not_logged_in(request):
    context = {
        'status': 'not-logged-in'
    }
    return render(request, 'not_logged_in.html', context)

@login_required
def homepage(request):
    #:
    kategori_list = Kategori.objects.all()

    if request.user.is_pengguna:
        # Misalkan hanya menampilkan subkategori yang cocok dengan pengguna
        subkategori_list = Subkategori.objects.filter(tipe='pengguna')  # Pastikan tipe ini sesuai kebutuhan Anda
    elif request.user.is_pekerja:
        # Menampilkan subkategori khusus untuk pekerja
        subkategori_list = Subkategori.objects.filter(tipe='pekerja')  # Pastikan tipe ini sesuai kebutuhan Anda
    else:
        # Jika tidak ada role yang cocok, tampilkan semua subkategori atau kosongkan
        subkategori_list = Subkategori.objects.none()  # Atau gunakan all() jika ingin menampilkan semuanya

    context = {
        'kategori_list': kategori_list,
        'subkategori_list': subkategori_list,
        'is_pengguna': request.user.is_pengguna,
        'is_pekerja': request.user.is_pekerja,
    }
    return render(request, 'homepage.html', context)
