from django.db import models

class Testimoni(models.Model):
    user = models.CharField(max_length=100)  # Nama pengguna sebagai string dummy
    rating = models.IntegerField()  # Rating, misal dari 1-5
    comment = models.TextField()  # Komentar yang diberikan
    date_created = models.DateTimeField(auto_now_add=True)  # Tanggal pembuatan testimoni

    def __str__(self):
        return f'{self.user} - {self.rating}'
