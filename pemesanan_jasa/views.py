from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from main.models import MyPay

@login_required
def create_order(request, sesi_id):
    if request.method == 'POST':
        total_payment = request.POST['total_payment']
        discount_code = request.POST.get('discount_code')
        payment_method = request.POST['payment_method']

        user_mypay = MyPay.objects.get(user=request.user)
        if user_mypay.balance >= float(total_payment):
            user_mypay.balance -= float(total_payment)
            user_mypay.save()

            # Create order
            order = Order.objects.create(
                user=request.user,
                sesi_layanan_id=sesi_id,
                total_payment=total_payment,
                discount_code=discount_code,
                payment_method=payment_method,
                status='Mencari Pekerja Terdekat'
            )
            return redirect('view_orders')
        else:
            return render(request, 'pemesanan/create_order.html', {'error': 'Saldo tidak cukup'})

    return render(request, 'pemesanan/create_order.html')

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'pemesanan/view_orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Mencari Pekerja Terdekat':
        user_mypay = MyPay.objects.get(user=request.user)
        user_mypay.balance += order.total_payment
        user_mypay.save()

        order.status = 'Dibatalkan'
        order.save()
        
        return redirect('view_orders')
    return render(request, 'pemesanan/view_orders.html', {'error': 'Pesanan tidak bisa dibatalkan'})
