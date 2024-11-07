from django.db import models
from django.contrib.auth.models import User
from subkategori_layanan.models import SesiLayanan

class Order(models.Model):
    STATUS_CHOICES = [
        ('Mencari Pekerja Terdekat', 'Mencari Pekerja Terdekat'),
        ('Menunggu Pembayaran', 'Menunggu Pembayaran'),
        ('Pesanan Selesai', 'Pesanan Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sesi_layanan = models.ForeignKey(SesiLayanan, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Mencari Pekerja Terdekat')
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=20, blank=True, null=True)
    payment_method = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.sesi_layanan.nama_layanan} - {self.status}"
