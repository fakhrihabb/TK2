
from lib2to3.fixes.fix_input import context

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Pengguna, Pekerja, User
from django.views.generic import CreateView
from .forms import PenggunaRegisterForm, PekerjaRegisterForm
from django.contrib.auth import logout

# Create your views here.

def register(request):
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('homepage')
    else:
        form = AuthenticationForm(request)
    context = {'form': form}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('authentication:login')

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
        return redirect('authentication:login')

class PekerjaRegisterView(CreateView):
    model = User
    form_class = PekerjaRegisterForm
    template_name = 'pekerja_register.html'
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'pekerja'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('authentication:login')
