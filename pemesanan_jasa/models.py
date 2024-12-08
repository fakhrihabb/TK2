# from django.db import models
# from django.conf import settings  # Untuk referensi model User
# import uuid

# class PemesananJasa(models.Model):
#     pengguna = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     tanggal_pemesanan = models.DateField()
#     diskon = models.CharField(max_length=20, blank=True, null=True)
#     total_pembayaran = models.DecimalField(max_digits=10, decimal_places=2)
#     metode_pembayaran = models.CharField(max_length=50)
#     # testimoni_dibuat = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Pesanan oleh {self.pengguna} pada {self.tanggal_pemesanan}"

# class StatusPesanan(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     status = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.status
    
# class TRPemesananStatus(models.Model):
#     id_tr_pemesanan = models.ForeignKey('PemesananJasa', on_delete=models.CASCADE)  # Relasi ke PemesananJasa
#     id_status = models.ForeignKey(StatusPesanan, on_delete=models.CASCADE)  # Relasi ke StatusPesanan
#     tgl_waktu = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('id_tr_pemesanan', 'id_status')  # Gabungan Primary Key

#     def __str__(self):
#         return f"{self.id_tr_pemesanan} - {self.id_status.status}"

