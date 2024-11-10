from django.shortcuts import render, redirect

from authentication.forms import PenggunaRegistrationForm

from django.contrib.auth import get_user_model

# Create your views here.
def register_pengguna(request):
    args = {}
    if request.method == "POST":
        form = PenggunaRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('authentication:login')
        return render(request, 'register.html', {'form': form})
    else:
        form = PenggunaRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    pass