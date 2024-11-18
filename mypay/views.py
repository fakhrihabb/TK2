from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from .models import Transaction

def mypay(request):
    balance = sum(transaction.amount for transaction in Transaction.objects.all())
    transactions = Transaction.objects.all()
    return render(request, 'mypay/mypay.html', {'balance': balance, 'transactions': transactions})

def transaksi(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        # Tambahkan transaksi baru
        Transaction.objects.create(category=category, amount=amount, description=description)
        return redirect('mypay:mypay')
    
    return render(request, 'mypay/transaksi.html')
