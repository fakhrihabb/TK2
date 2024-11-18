from django.shortcuts import get_object_or_404, render, redirect
from .forms import PemesananForm
from .models import PemesananJasa



def create_pemesanan(request):
    harga_dasar = 100000  # Harga dasar layanan, misalnya Rp 100.000

    if request.method == 'POST':
        form = PemesananForm(request.POST)
        
        if form.is_valid():
            pesanan = form.save(commit=False)
            pesanan.total_pembayaran = harga_dasar  # Set harga dasar

            # Cek apakah ada diskon
            kode_diskon = form.cleaned_data.get('diskon')
            if kode_diskon == "DISKON10":  # Contoh diskon
                pesanan.total_pembayaran *= 0.9  # Mengurangi 10%
            
            pesanan.save()
            
            return redirect('view_pemesanan')  # Redirect ke halaman pesanan
    else:
        form = PemesananForm()
    
    return render(request, 'create_pemesanan.html', {'form': form, 'harga_dasar': harga_dasar})


def view_pemesanan(request):
    daftar_pesanan = PemesananJasa.objects.all()  # Ambil semua data pesanan atau sesuai kebutuhan
    context = {
        'daftar_pesanan': daftar_pesanan
    }
    return render(request, 'view_pemesanan.html', context)

def delete_pemesanan(request, pk):
    pesanan = get_object_or_404(PemesananJasa, pk=pk)
    pesanan.delete()
    return redirect('view_pemesanan')  # Mengarahkan kembali ke halaman daftar pemesanan