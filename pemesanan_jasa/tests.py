from django.test import TestCase

# Create your tests here.
from django.db import models
from django.contrib.auth.models import User

class PemesananJasa(models.Model):
    STATUS_CHOICES = [
        ('Menunggu Pembayaran', 'Menunggu Pembayaran'),
        ('Mencari Pekerja Terdekat', 'Mencari Pekerja Terdekat'),
        ('Pesanan Selesai', 'Pesanan Selesai'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tanggal_pemesanan = models.DateField(auto_now_add=True)
    diskon = models.CharField(max_length=50, blank=True, null=True)
    total_pembayaran = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Menunggu Pembayaran')
    
    def __str__(self):
        return f"Pemesanan oleh {self.user.username} - {self.status}"
