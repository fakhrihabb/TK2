# main/models.py
from django.db import models

class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Subkategori(models.Model):
    nama = models.CharField(max_length=255)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    tipe = models.CharField(max_length=50, choices=(('pengguna', 'Pengguna'), ('pekerja', 'Pekerja')))
    
    def __str__(self):
        return self.nama
