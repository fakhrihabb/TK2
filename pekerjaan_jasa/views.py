from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponseNotFound
from django.urls import reverse
from django.db import connection
from django.contrib import messages
from authentication.views import get_user

# Helper function to execute raw SQL queries
def execute_sql(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if query.strip().lower().startswith("select"):
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return None

# View untuk menampilkan job orders, termasuk form filter kategori dan subkategori
def pekerjaan_jasa(request):
    categories = execute_sql("SELECT * FROM pekerjaan_jasa_servicecategory")
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')

    # Filter pesanan berdasarkan kategori dan subkategori jika ada
    orders_query = "SELECT * FROM pekerjaan_jasa_serviceorder WHERE status = %s"
    orders_params = ['mencari']

    if selected_category:
        orders_query += " AND subcategory_id IN (SELECT id FROM pekerjaan_jasa_servicesubcategory WHERE category_id = %s)"
        orders_params.append(selected_category)

    if selected_subcategory:
        orders_query += " AND subcategory_id = %s"
        orders_params.append(selected_subcategory)

    orders = execute_sql(orders_query, orders_params)

    # Subkategori untuk dropdown
    subcategories = []
    if selected_category:
        subcategories = execute_sql("SELECT * FROM pekerjaan_jasa_servicesubcategory WHERE category_id = %s", [selected_category])

    # URL untuk mendapatkan subcategories
    get_subcategories_url = reverse('pekerjaan_jasa:get_subcategories', kwargs={'category_id': 0}).replace('0', '%s')

    user = get_user(request)
    return render(request, 'pekerjaan_jasa/urutan_pekerjaan.html', {
        'categories': categories,
        'orders': orders,
        'subcategories': subcategories,
        'get_subcategories_url': get_subcategories_url,
        'user': user
    })

# View untuk status pekerjaan
def job_status(request):
    categories = execute_sql("SELECT * FROM pekerjaan_jasa_servicecategory")
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')

    # Ambil pesanan dengan status selain 'dibatalkan'
    orders_query = "SELECT * FROM pekerjaan_jasa_serviceorder WHERE status != %s"
    orders_params = ['dibatalkan']

    if selected_category:
        orders_query += " AND subcategory_id IN (SELECT id FROM pekerjaan_jasa_servicesubcategory WHERE category_id = %s)"
        orders_params.append(selected_category)

    if selected_subcategory:
        orders_query += " AND subcategory_id = %s"
        orders_params.append(selected_subcategory)

    orders = execute_sql(orders_query, orders_params)

    # Subkategori untuk dropdown
    subcategories = []
    if selected_category:
        subcategories = execute_sql("SELECT * FROM pekerjaan_jasa_servicesubcategory WHERE category_id = %s", [selected_category])

    get_subcategories_url = reverse('pekerjaan_jasa:get_subcategories', kwargs={'category_id': 0}).replace('0', '%s')

    user = get_user(request)
    return render(request, 'pekerjaan_jasa/status_pekerjaan.html', {
        'categories': categories,
        'subcategories': subcategories,
        'orders': orders,
        'get_subcategories_url': get_subcategories_url,
        'user': user
    })

# View untuk memperbarui status pekerjaan
def update_status(request, order_id, new_status):
    valid_transitions = {
        "menunggu": "tiba",
        "tiba": "dilakukan",
        "dilakukan": "selesai",
    }

    # Ambil status pesanan saat ini
    current_status_query = "SELECT status FROM pekerjaan_jasa_serviceorder WHERE id = %s"
    current_status_result = execute_sql(current_status_query, [order_id])

    if not current_status_result:
        return HttpResponseNotFound("Pesanan tidak ditemukan.")

    current_status = current_status_result[0]['status']

    # Validasi transisi status
    if new_status != valid_transitions.get(current_status):
        return HttpResponseNotFound("Transisi status tidak valid.")

    # Update status pesanan
    update_query = "UPDATE pekerjaan_jasa_serviceorder SET status = %s WHERE id = %s"
    execute_sql(update_query, [new_status, order_id])

    return redirect('pekerjaan_jasa:job-status')

# View untuk mendapatkan subcategories berdasarkan kategori
def get_subcategories(request, category_id):
    try:
        subcategories = execute_sql("SELECT id, name FROM pekerjaan_jasa_servicesubcategory WHERE category_id = %s", [category_id])
        return JsonResponse(subcategories, safe=False)
    except Exception:
        return JsonResponse([], safe=False)

# View untuk memindahkan pesanan ke status 'menunggu'
def move_to_status(request, order_id):
    order_query = "SELECT status FROM pekerjaan_jasa_serviceorder WHERE id = %s"
    order_result = execute_sql(order_query, [order_id])

    if not order_result:
        return HttpResponseNotFound("Pesanan tidak ditemukan.")

    if order_result[0]['status'] == 'mencari':
        update_query = "UPDATE pekerjaan_jasa_serviceorder SET status = 'menunggu' WHERE id = %s"
        execute_sql(update_query, [order_id])
    else:
        messages.error(request, 'Pesanan sudah dipindahkan sebelumnya!')
    return redirect('pekerjaan_jasa:pekerjaan_jasa')

# View untuk menerima pesanan
def accept_order(request, order_id):
    order_result = execute_sql("SELECT * FROM pekerjaan_jasa_serviceorder WHERE id = %s", [order_id])

    if not order_result:
        raise Http404("Order not found")

    if not getattr(request.user, 'is_worker', False):
        messages.error(request, "You are not authorized to accept orders.")
        return redirect('pekerjaan_jasa:pekerjaan_jasa')

    update_query = "UPDATE pekerjaan_jasa_serviceorder SET status = %s, assigned_worker_id = %s WHERE id = %s"
    execute_sql(update_query, ['menunggu', request.user.id, order_id])
    return redirect('pekerjaan_jasa:pekerjaan_jasa')
