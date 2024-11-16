from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import ServiceCategory, ServiceOrder
from django.http import JsonResponse
from .models import ServiceSubcategory
from django.core.serializers import serialize

# View untuk menampilkan job orders, termasuk form filter kategori dan subkategori
def pekerjaan_jasa(request):
    categories = ServiceCategory.objects.all()  # Ambil semua kategori
    subcategories = ServiceSubcategory.objects.all()
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')

    # Ambil daftar order berdasarkan filter
    orders = ServiceOrder.objects.filter(status='mencari')
    if selected_category:
        orders = orders.filter(subcategory__category__id=selected_category)
    if selected_subcategory:
        orders = orders.filter(subcategory_id=selected_subcategory)

    # Ambil subkategori berdasarkan kategori yang dipilih
    subcategories = ServiceSubcategory.objects.filter(category_id=selected_category) if selected_category else []

    # Serialisasi subcategories menjadi JSON-friendly format
    subcategory_data = serialize('json', subcategories)

    return render(request, 'pekerjaan_jasa/urutan_pekerjaan.html', {
        'categories': categories,
        'orders': orders,
        'subcategories': subcategory_data  # Kirimkan data subkategori yang sudah diserialisasi
    }
    )


# View untuk menerima pesanan (mengubah status dan menetapkan pekerja)
def accept_order(request, order_id):
    try:
        order = ServiceOrder.objects.get(id=order_id)
    except ServiceOrder.DoesNotExist:
        raise Http404("Order not found")
    
    order.status = 'menunggu'
    order.assigned_worker = request.user
    order.save()
    return redirect('pekerjaan_jasa:pekerjaan_jasa')  # Pastikan nama URL-nya sesuai

# View untuk status pekerjaan
def job_status(request):
    jobs = ServiceOrder.objects.filter(assigned_worker=request.user).exclude(status__in=['selesai', 'dibatalkan'])
    return render(request, 'pekerjaan_jasa/status_pekerjaan.html', {'jobs': jobs})

# View untuk memperbarui status pekerjaan
def update_status(request, order_id, new_status):
    try:
        order = ServiceOrder.objects.get(id=order_id, assigned_worker=request.user)
    except ServiceOrder.DoesNotExist:
        raise Http404("Order not found")

    order.status = new_status
    order.save()
    return redirect('pekerjaan_jasa:job_status')  # Pastikan nama URL-nya sesuai

# View untuk mendapatkan subcategories berdasarkan kategori
def get_subcategories(request, category_id):
    try:
        # Ambil subcategories berdasarkan kategori
        subcategories = ServiceSubcategory.objects.filter(category_id=category_id)
        # Serialisasi data menjadi JSON-friendly format
        subcategory_data = [{"id": sub.id, "name": sub.name} for sub in subcategories]
        return JsonResponse(subcategory_data, safe=False)  # Kirim data sebagai JSON
    except ServiceSubcategory.DoesNotExist:
        return JsonResponse([], safe=False)  # Jika tidak ada subkategori, kirimkan array kosong
