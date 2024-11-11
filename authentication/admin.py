from django.contrib import admin
from authentication.models import User, Pekerja, Pengguna
# Register your models here.

admin.site.register(Pekerja)
admin.site.register(Pengguna)
admin.site.register(User)