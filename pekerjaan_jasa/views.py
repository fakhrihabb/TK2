from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import ServiceCategory, ServiceOrder
from django.http import JsonResponse
from .models import ServiceSubcategory
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseNotFound, JsonResponse

# View untuk menampilkan job orders, termasuk form filter kategori dan subkategori
def pekerjaan_jasa(request):
    categories = ServiceCategory.objects.all()
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')

    # Filter pesanan berdasarkan kategori dan subkategori jika ada
    orders = ServiceOrder.objects.filter(status='mencari')
    if selected_category:
        orders = orders.filter(subcategory__category_id=selected_category)
    if selected_subcategory:
        orders = orders.filter(subcategory_id=selected_subcategory)

    # Validasi kategori dan subkategori
    if selected_category and not ServiceCategory.objects.filter(id=selected_category).exists():
        selected_category = None
    if selected_subcategory and not ServiceSubcategory.objects.filter(id=selected_subcategory).exists():
        selected_subcategory = None

    # Subkategori untuk dropdown
    subcategories = ServiceSubcategory.objects.filter(category_id=selected_category) if selected_category else []

    # Kirimkan URL ke template
    get_subcategories_url = reverse('pekerjaan_jasa:get_subcategories', kwargs={'category_id': 0}).replace('0', '%s')

    return render(request, 'pekerjaan_jasa/urutan_pekerjaan.html', {
        'categories': categories,
        'orders': orders,
        'subcategories': subcategories,
        'get_subcategories_url': get_subcategories_url,
    })


# View untuk status pekerjaan
def job_status(request):
    categories = ServiceCategory.objects.all()
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')  # Tambahkan ini untuk mengambil subkategori yang dipilih

    # Ambil pesanan dengan status 'menunggu'
    orders = ServiceOrder.objects.exclude(status="dibatalkan")
    if selected_category:
        orders = orders.filter(subcategory__category_id=selected_category)
    if selected_subcategory:  # Sekarang aman karena variabel sudah didefinisikan
        orders = orders.filter(subcategory_id=selected_subcategory)

    # Validasi kategori dan subkategori
    if selected_category and not ServiceCategory.objects.filter(id=selected_category).exists():
        selected_category = None
    if selected_subcategory and not ServiceSubcategory.objects.filter(id=selected_subcategory).exists():
        selected_subcategory = None

    subcategories = ServiceSubcategory.objects.filter(category_id=selected_category) if selected_category else []

    get_subcategories_url = reverse('pekerjaan_jasa:get_subcategories', kwargs={'category_id': 0}).replace('0', '%s')

    return render(request, 'pekerjaan_jasa/status_pekerjaan.html', {
        'categories': categories,
        'subcategories': subcategories,
        'orders': orders,
        'get_subcategories_url': get_subcategories_url,
    })



# View untuk memperbarui status pekerjaan
def update_status(request, order_id, new_status):
    # Dapatkan pesanan berdasarkan ID
    order = get_object_or_404(ServiceOrder, id=order_id)
    
    # Validasi transisi status
    valid_transitions = {
        "menunggu": "tiba",
        "tiba": "dilakukan",
        "dilakukan": "selesai",
    }

    # Cek apakah transisi valid
    if new_status != valid_transitions.get(order.status):
        return HttpResponseNotFound("Transisi status tidak valid.")

    # Update status pesanan
    order.status = new_status
    order.save()

    # Redirect kembali ke halaman job-status
    return redirect('pekerjaan_jasa:job-status')

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

def move_to_status(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    if order.status == 'mencari':
        order.status = 'menunggu'
        order.save()
    else:
        messages.error(request, 'Pesanan sudah dipindahkan sebelumnya!')
    return redirect('pekerjaan_jasa:pekerjaan_jasa')

def accept_order(request, order_id):
    try:
        order = ServiceOrder.objects.get(id=order_id)
    except ServiceOrder.DoesNotExist:
        raise Http404("Order not found")
    
    # Pastikan hanya pekerja dengan role tertentu yang bisa menerima order
    if not request.user.is_worker:
        messages.error(request, "You are not authorized to accept orders.")
        return redirect('pekerjaan_jasa:pekerjaan_jasa')
    
    order.status = 'menunggu'
    order.assigned_worker = request.user
    order.save()
    return redirect('pekerjaan_jasa:pekerjaan_jasa')
