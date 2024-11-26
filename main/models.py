from django.conf import settings
from django.db import models

# class CustomUser(AbstractUser):
#     @property
#     def is_pengguna(self):
#         return self.groups.filter(name='Pengguna').exists()
    
#     @property
#     def is_pekerja(self):
#         return self.groups.filter(name='Pekerja').exists()

# # Menggunakan settings.AUTH_USER_MODEL untuk mengacu pada model pengguna yang dapat dikustomisasi
# class Profile(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

# class ServiceOrder(models.Model):
#     assigned_worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

# class TransactionHistory(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
