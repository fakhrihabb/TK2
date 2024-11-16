from django.db import models
from authentication.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ServiceSubcategory(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ServiceOrder(models.Model):
    STATUS_CHOICES = [
        ('mencari', 'Mencari Pekerja Terdekat'),
        ('menunggu', 'Menunggu Pekerja Berangkat'),
        ('tiba', 'Pekerja Tiba Di Lokasi'),
        ('dilakukan', 'Pelayanan Jasa Sedang Dilakukan'),
        ('selesai', 'Pesanan Selesai'),
        ('dibatalkan', 'Pesanan Dibatalkan'),
    ]

    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    order_date = models.DateField()
    work_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='mencari')
    assigned_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order: {self.customer_name} - {self.subcategory.name} ({self.get_status_display()})"

class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('TOP UP', 'Top Up'),
        ('PAY SERVICE', 'Pay Service'),
        ('TRANSFER', 'Transfer'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    service_name = models.CharField(max_length=100, null=True, blank=True)
    recipient_phone = models.CharField(max_length=15, null=True, blank=True)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.user.username}"
