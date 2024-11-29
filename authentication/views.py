from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy, reverse
from django.db import connection

from .models import Pengguna, Pekerja, User
from django.views.generic import CreateView, UpdateView
from .forms import PenggunaRegisterForm, PekerjaRegisterForm, UpdatePekerjaForm, UpdateUserForm, UserLoginForm
from django.contrib.auth import logout

# Create your views here.

def register(request):
    return render(request, 'register.html')

def register_pengguna(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            email = request.POST['email']

def login_user(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        # Check if a user with the provided phone no exists
        if not User.objects.filter(phone_number=phone_number).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Phone Number')
            return redirect('authentication:login')

        # Authenticate the user with the provided phone no and password
        user = authenticate(phone_number=phone_number, password=password)

        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('authentication:login')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('homepage')

    # Render the login page template (GET request)
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


# class PenggunaRegisterView(CreateView):
#     model = User
#     form_class = PenggunaRegisterForm
#     template_name = 'pengguna_register.html'
#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'pengguna'
#         return super().get_context_data(**kwargs)
#
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         return redirect('authentication:view_profile')
#
# class PekerjaRegisterView(CreateView):
#     model = User
#     form_class = PekerjaRegisterForm
#     template_name = 'pekerja_register.html'
#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'pekerja'
#         return super().get_context_data(**kwargs)
#
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         return redirect('homepage')