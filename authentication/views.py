from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy, reverse
from .models import Pengguna, Pekerja, User
from django.views.generic import CreateView, UpdateView
from .forms import PenggunaRegisterForm, PekerjaRegisterForm, UpdatePekerjaForm, UpdateUserForm, UserLoginForm
from django.contrib.auth import logout
from django.db import connection

# Create your views here.

def register(request):
    return render(request, 'register.html')


def login_user(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # Cek apakah user ada di authentication_user
        user = authenticate(phone_number=phone_number, password=password)

        if user:
            # Cek apakah user sudah terdaftar di profil_pekerja
            query_check = "SELECT COUNT(*) FROM profil_pekerja WHERE user_id = %s"
            with connection.cursor() as cursor:
                cursor.execute(query_check, [user.id])
                result = cursor.fetchone()

            if result[0] == 0:  # Jika belum ada, tambahkan
                query_insert = """
                    INSERT INTO profil_pekerja (id, user_id, nama, nama_bank, nomor_rekening, rating, jml_pesanan_selesai)
                    VALUES (gen_random_uuid(), %s, %s, 'Bank Mandiri', '123456789', 4.5, 0)
                """
                with connection.cursor() as cursor:
                    cursor.execute(query_insert, [
                        user.id,
                        f"{user.first_name} {user.last_name}"
                    ])
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, "Invalid Phone Number or Password")
            return redirect('authentication:login')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('authentication:login')

@login_required
def view_profile(request):
    user = request.user
    return render(request, "profile.html", context={'user': user})

def update_pekerja(request):
    if request.method == 'POST':
        pekerja_form = UpdatePekerjaForm(request.POST, instance=request.user.pekerja)
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if pekerja_form.is_valid() and user_form.is_valid():
            pekerja_form.save()
            user_form.save()
            return redirect('homepage')
    else:
        pekerja_form = UpdatePekerjaForm(instance=request.user.pekerja)
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'edit_pekerja.html', {'u_form': user_form,'p_form': pekerja_form})

def update_pengguna(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('authentication:view_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'edit_pengguna.html', {'u_form': user_form})


class PenggunaRegisterView(CreateView):
    model = User
    form_class = PenggunaRegisterForm
    template_name = 'pengguna_register.html'
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'pengguna'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('authentication:view_profile')

class PekerjaRegisterView(CreateView):
    model = User
    form_class = PekerjaRegisterForm
    template_name = 'pekerja_register.html'

    def form_valid(self, form):
        user = form.save()
        print(f"User berhasil dibuat: {user.id}, {user.phone_number}")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO profil_pekerja (id, user_id, nama, phone_number, nama_bank, nomor_rekening, rating, jml_pesanan_selesai)
                    VALUES (
                        gen_random_uuid(), 
                        %s, 
                        %s, 
                        %s, 
                        %s, 
                        %s, 
                        %s, 
                        %s
                    )
                """, [
                    user.id,
                    f"{user.first_name} {user.last_name}",
                    user.phone_number,
                    "Bank Default",
                    "0000000000",
                    0,
                    0
                ])

                print("Pekerja berhasil ditambahkan ke profil_pekerja")
        except Exception as e:
            print(f"Error: {e}")
        login(self.request, user)
        return redirect('homepage')
