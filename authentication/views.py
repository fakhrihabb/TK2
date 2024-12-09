import uuid

from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Pengguna, Pekerja, User
from django.views.generic import CreateView, UpdateView
from .forms import PenggunaRegisterForm, PekerjaRegisterForm, UpdatePekerjaForm, UpdateUserForm, UserLoginForm
from django.db import connection

def login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.session.get('phone_number', 'not found') == 'not found' or request.session.get('is_pekerja', 'not found') == 'not found' or request.session['user_id'] == 'not found':
            return redirect('not_logged_in')
        else:
            return view_func(request, *args, **kwargs)
    return wrap

def register(request):
    try:
        user = get_user(request)
        return render(request, 'register.html', context={'user': user})
    except Exception as e:
        return render(request, 'register.html', context={'error': e})

@csrf_exempt
def register_pengguna(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        birth_date = request.POST['birth_date']
        address = request.POST['address']
        user_id = uuid.uuid4()
        if not (phone_number and password and first_name and last_name and gender and birth_date and address):
            return render(request, 'pengguna_register.html', {'messages':['Semua field harus diisi']})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                # insert ke tabel user
                cursor.execute("""
                INSERT INTO "USER" (id, first_name, last_name, gender, phone_number, password, birth_date, address, is_pekerja)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '0')
                """, [user_id, first_name, last_name, gender, phone_number, password, birth_date, address])
                # insert ke tabel pengguna
                cursor.execute("""
                INSERT INTO "PENGGUNA" (user_id)
                VALUES (%s)
                """, [user_id])
                return redirect('authentication:login')
        except Exception as e:
            return render(request, 'pengguna_register.html', {'messages':[str(e)]})

    return render(request, 'pengguna_register.html')

@csrf_exempt
def register_pekerja(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        birth_date = request.POST['birth_date']
        address = request.POST['address']
        user_id = uuid.uuid4()
        bank = request.POST['bank']
        bank_number = request.POST['bank_number']
        npwp = request.POST['npwp']
        image_url = request.POST['image_url']

        if not (phone_number and password and first_name and last_name and gender and birth_date and address and bank and bank_number and npwp and image_url):
            return render(request, 'pekerja_register.html', {'messages': ['Semua field harus diisi']})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                # insert ke tabel user
                cursor.execute("""
                INSERT INTO "USER" (id, first_name, last_name, gender, phone_number, password, birth_date, address, is_pekerja)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '1')
                """, [user_id, first_name, last_name, gender, phone_number, password, birth_date, address])
                # insert ke tabel pekerja
                cursor.execute("""
                INSERT INTO "PEKERJA" (user_id, bank, bank_number, npwp, image_url)
                VALUES (%s, %s, %s, %s, %s)
                """, [user_id, bank, bank_number, npwp, image_url])
                return redirect('authentication:login')
        except Exception as e:
            return render(request, 'pekerja_register.html', {'messages': [str(e)]})

    return render(request, 'pekerja_register.html')

@csrf_exempt
def login(request):
    request.session['phone_number'] = 'not found'
    request.session['is_pekerja'] = 'not found'
    request.session['user_id'] = 'not found'

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                cursor.execute("""
                SELECT phone_number, is_pekerja, id
                FROM "USER"
                WHERE phone_number = %s AND password = %s 
                """, [phone_number, password])
                result = cursor.fetchone()
                if result:
                    request.session['phone_number'] = result[0]
                    request.session['is_pekerja'] = result[1]
                    request.session['user_id'] = str(result[2])
                    return redirect('homepage')
                else:
                    messages.error(request, 'Wrong phone number or password')


        except Exception as e:
            messages.error(request, 'Error occured: ' + str(e))

        return render(request, 'login.html')
    return render(request, 'login.html')


def logout(request):
    request.session['phone_number'] = 'not found'
    request.session['is_pekerja'] = 'not found'
    request.session['user_id'] = 'not found'
    print("setelah logout")
    response = redirect('authentication:login')
    return response

def get_user(request):
    """This function must be used within a view with @login_required decorator"""
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO public")
        cursor.execute("""
        SELECT first_name, last_name, gender, phone_number, birth_date, address, is_pekerja, saldo
        FROM "USER"
        WHERE id = %s
        """, [request.session['user_id']])
        user_result = cursor.fetchone()
        if user_result:
            name = user_result[0] + " " + user_result[1]
            gender = user_result[2]
            phone_number = user_result[3]
            birth_date = user_result[4]
            address = user_result[5]
            is_pekerja = user_result[6]
            saldo = user_result[7]
            additional_infos = []
            if is_pekerja:
                cursor.execute("""
                SELECT bank, bank_number, npwp, image_url, rating, order_complete, id
                FROM "PEKERJA"
                WHERE user_id = %s
                """, [request.session['user_id']])
                pekerja_result = cursor.fetchone()
                bank = pekerja_result[0]
                bank_number = pekerja_result[1]
                npwp = pekerja_result[2]
                image_url = pekerja_result[3]
                rating = pekerja_result[4]
                order_complete = pekerja_result[5]
                id_pekerja = pekerja_result[6]
                additional_infos = [bank, bank_number, npwp, image_url, rating, order_complete, id_pekerja]
            else:
                cursor.execute("""
                SELECT level, id
                FROM "PENGGUNA"
                WHERE user_id = %s
                """, [request.session['user_id']])
                pengguna_result = cursor.fetchone()
                level = pengguna_result[0]
                id_pengguna = pengguna_result[1]
                additional_infos = [level, id_pengguna]
            return {
                'id': request.session['user_id'],
                'name': name,
                'gender': gender,
                'phone_number': phone_number,
                'birth_date': birth_date,
                'address': address,
                'is_pekerja': is_pekerja,
                'saldo': saldo,
                'additional_infos': additional_infos,
                'logged_in': True,
            }
        else:
            return {
                'logged_in': False,
            }

@login_required
def view_profile(request):
    user = get_user(request)
    return render(request, "profile.html", context={'user': user})

@login_required
def update_pekerja(request):
    current_user = get_user(request)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        birth_date = request.POST['birth_date']
        address = request.POST['address']
        bank = request.POST['bank']
        bank_number = request.POST['bank_number']
        npwp = request.POST['npwp']
        image_url = request.POST['image_url']

        if not (
                phone_number and first_name and last_name and gender and birth_date and address and bank and bank_number and npwp and image_url):
            return render(request, 'edit_pekerja.html', {'messages': ['Semua field harus diisi'], 'user': current_user})
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                # update tabel user
                cursor.execute("""
                UPDATE "USER"
                SET first_name = %s, last_name = %s, gender = %s, phone_number = %s, birth_date = %s, address = %s
                WHERE id = %s
                """, [first_name, last_name, gender, phone_number, birth_date, address, request.session['user_id']])
                # update tabel pekerja
                cursor.execute("""
                UPDATE "PEKERJA"
                SET bank = %s, bank_number = %s, npwp = %s, image_url = %s
                WHERE user_id = %s
                """, [bank, bank_number, npwp, image_url, request.session['user_id']])
                return redirect('authentication:view_profile')
        except Exception as e:
            return render(request, 'edit_pekerja.html', {'messages': [str(e)], 'user': current_user})

    return render(request, 'edit_pekerja.html', context={'user': current_user})


@login_required
def update_pengguna(request):
    current_user = get_user(request)
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        phone_number = request.POST['phone_number']
        birth_date = request.POST['birth_date']
        address = request.POST['address']

        if not (
                phone_number and first_name and last_name and gender and birth_date and address):
            return render(request, 'edit_pengguna.html', {'messages': ['Semua field harus diisi'], 'user': current_user})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")
                # update tabel user
                cursor.execute("""
                UPDATE "USER"
                SET first_name = %s, last_name = %s, gender = %s, phone_number = %s, birth_date = %s, address = %s
                WHERE id = %s
                """, [first_name, last_name, gender, phone_number, birth_date, address, request.session['user_id']])
                return redirect('authentication:view_profile')
        except Exception as e:
            return render(request, 'edit_pengguna.html', {'messages': [str(e)], 'user': current_user})

    return render(request, 'edit_pengguna.html', context={'user': current_user})