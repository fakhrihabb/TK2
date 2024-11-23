from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# class Profile(models.Model):
#     class Gender(models.TextChoices):
#         MALE = 'L', 'LAKI-LAKI'
#         FEMALE = 'P', 'PEREMPUAN'
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
#     phone_no = models.CharField(max_length=20, unique=True)
#     birth_date = models.DateField(null=True, blank=True)
#     address = models.CharField(max_length=100, null=True, blank=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

# class Pengguna(models.Model):
#     # TODO: implement derived level dari transaksi
#     level = 0
#
# class Pekerja(models.Model):
#     BANK_CHOICES = (
#         ('GoPay', 'GoPay'),
#         ('OVO', 'OVO'),
#         ('Virtual Account BCA', 'Virtual Account BCA'),
#         ('Virtual Account BNI', 'Virtual Account BNI'),
#         ('Virtual Account Mandiri', 'Virtual Account Mandiri'),
#     )
#     bank = models.CharField(max_length=23, choices=BANK_CHOICES, default='GoPay')
#     bank_number = models.CharField(max_length=20, unique=True)
#     npwp = models.CharField(max_length=16)
#     image_url = models.URLField(null=True, blank=True)
#     created_by = models.ForeignKey('Profiles', on_delete=models.CASCADE, related_name='created_by')
#     class Meta:
#         unique_together = ('bank', 'bank_number')
#
# class Profiles(AbstractUser):
#     GENDER_CHOICES = (
#         ('L', 'Laki'),
#         ('P', 'Perempuan'),
#     )
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='L')
#     phone_number = models.CharField(max_length=20, unique=True)
#     birth_date = models.DateField()
#     address = models.CharField(max_length=100)
#     pekerja = models.OneToOneField(Pekerja, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Pekerja')
#     pengguna = models.OneToOneField(Pengguna, on_delete = models.CASCADE, null=True, blank=True, verbose_name='Pengguna')
#
#     class Meta:
#         db_table = 'profiles'
#         verbose_name = 'Profile'
#         verbose_name_plural = 'Profiles'
#
#     def is_pekerja(self):
#         if self.pekerja:
#             return True
#         else:
#             return False
#
#     def is_pengguna(self):
#         if self.pengguna:
#             return True
#         else:
#             return False
#
#     def __str__(self):
#         return self.username


class User(AbstractUser):
    is_pengguna = models.BooleanField(default=False)
    is_pekerja = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    GENDER_CHOICES = (
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='L')
    phone_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField()
    address = models.CharField(max_length=100)
    saldo_mypay = models.IntegerField(default=0)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'address', 'gender', 'birth_date']

class Pengguna(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    level = 0

    def __str__(self):
        return self.user.username

class Pekerja(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    BANK_CHOICES = (
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('Virtual Account BCA', 'Virtual Account BCA'),
        ('Virtual Account BNI', 'Virtual Account BNI'),
        ('Virtual Account Mandiri', 'Virtual Account Mandiri'),
    )
    bank = models.CharField(max_length=23, choices=BANK_CHOICES, default='GoPay')
    bank_number = models.CharField(max_length=20)
    npwp = models.CharField(max_length=16)
    image_url = models.URLField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bank', 'bank_number'], name='bank constraint')
        ]

    def __str__(self):
        return self.user.username