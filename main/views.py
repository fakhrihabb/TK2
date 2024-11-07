from django.shortcuts import render
from subkategori_layanan.models import Kategori, Subkategori  # Import models from subkategori app

def homepage(request):
    kategori_list = Kategori.objects.all()
    subkategori_list = Subkategori.objects.all()
    context = {
        'kategori_list': kategori_list,
        'subkategori_list': subkategori_list,
    }
    return render(request, 'homepage.html', context)
