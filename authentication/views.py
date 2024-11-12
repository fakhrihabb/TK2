from lib2to3.fixes.fix_input import context

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Pengguna, Pekerja, User
from django.views.generic import CreateView
from .forms import PenggunaRegisterForm, PekerjaRegisterForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def homepage(request):
    # Check the role of the authenticated user
    if request.user.is_pengguna:
        return redirect('subkategori_pengguna')  # Redirect to pengguna-specific page
    elif request.user.is_pekerja:
        return redirect('subkategori_pekerja')  # Redirect to pekerja-specific page
    else:
        # If the user has no specific role, display a generic error or homepage
        return render(request, 'homepage.html')

def register(request):
    return render(request, 'register.html')

@csrf_exempt
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
        user = form.save(commit=False)
        user.is_pengguna = True  # Set sebagai pengguna
        user.save()
        login(self.request, user)
        return redirect('authentication:login')

class PekerjaRegisterView(CreateView):
    form_class = PekerjaRegisterForm
    template_name = 'pekerja_register.html'

    def form_valid(self, form):
        user = form.save(commit=True)  # Pastikan commit=True
        login(self.request, user)
        return redirect('authentication:login')
