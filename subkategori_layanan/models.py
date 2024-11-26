from django.db import models
from django.conf import settings
from django.db import models
import uuid

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

    tipe = models.CharField(max_length=10)
    deskripsi = models.TextField(default="Deskripsi belum tersedia.")

    def __str__(self):
        return self.nama

class SesiLayanan(models.Model):
    subkategori = models.ForeignKey('subkategori_layanan.Subkategori', on_delete=models.CASCADE)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    sesi = models.IntegerField()

    def __str__(self):
        return f"Sesi {self.sesi} - Harga: {self.harga} - Subkategori: {self.subkategori.nama}"

