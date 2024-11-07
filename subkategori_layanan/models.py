from django.db import models
from django.contrib.auth.models import User

class Kategori(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama


class Pekerja(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Subkategori(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama

class SesiLayanan(models.Model):
    subkategori = models.ForeignKey(Subkategori, on_delete=models.CASCADE)
    nama_layanan = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nama_layanan

class Testimoni(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Pengguna yang memberikan testimoni
    subkategori = models.ForeignKey(Subkategori, on_delete=models.CASCADE)  # Subkategori terkait
    rating = models.IntegerField()  # Misalnya skala 1-5
    komentar = models.TextField()  # Teks testimoni
    tanggal = models.DateTimeField(auto_now_add=True)  # Tanggal testimoni dibuat

    def __str__(self):
        return f"{self.user.username} - {self.subkategori.nama} - Rating: {self.rating}"