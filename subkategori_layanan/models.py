from django.db import models
from django.conf import settings

from django.db import models


class Kategori(models.Model):
    nama = models.CharField(max_length=100)

class Pekerja(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    
    def __str__(self):
        return self.nama

class Subkategori(models.Model):
    nama = models.CharField(max_length=100)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    TIPE_CHOICES = [
        ('pengguna', 'Pengguna'),
        ('pekerja', 'Pekerja'),
    ]
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES, default='pengguna')

    def __str__(self):
        return self.nama

class SesiLayanan(models.Model):
    subkategori = models.ForeignKey(Subkategori, on_delete=models.CASCADE)
    nama_layanan = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nama_layanan
