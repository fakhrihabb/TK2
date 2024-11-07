from django.db import models

class PemesananJasa(models.Model):
    STATUS_CHOICES = [
        ('menunggu_pembayaran', 'Menunggu Pembayaran'),
        ('mencari_pekerja', 'Mencari Pekerja Terdekat'),
        ('selesai', 'Pesanan Selesai'),
        ('dalam_proses', 'Dalam Proses'),
    ]

    tanggal_pemesanan = models.DateField()
    diskon = models.CharField(max_length=20, blank=True, null=True)
    total_pembayaran = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pembayaran = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='dalam_proses')
    testimoni_dibuat = models.BooleanField(default=False)

    def __str__(self):
        return f"Pesanan pada {self.tanggal_pemesanan} - Status: {self.status}"
