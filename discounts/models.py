from django.db import models

class Voucher(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    potongan = models.DecimalField(max_digits=10, decimal_places=2)
    min_transaksi = models.DecimalField(max_digits=10, decimal_places=2)
    jumlah_hari_berlaku = models.IntegerField()
    kuota_penggunaan = models.IntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.kode

class Promo(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    tanggal_akhir_berlaku = models.DateField()

    def __str__(self):
        return self.kode
