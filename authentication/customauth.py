from django.db import connection

class Profile:
    def __init__(self, first_name, last_name, gender, phone_number, birth_date, address):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.gender = gender
        self.phone_number = phone_number
        self.birth_date = birth_date
        self.address = address

class Pengguna(Profile):
    def __init__(self, first_name, last_name, gender, phone_number, birth_date, address):
        super().__init__(first_name, last_name, gender, phone_number, birth_date, address)
        self.is_pekerja = False
        self.level = 0

class Pekerja(Profile):
    def __init__(self, first_name, last_name, gender, phone_number, birth_date, address, bank, bank_number, npwp, image_url):
        super().__init__(first_name, last_name, gender, phone_number, birth_date, address)
        self.is_pekerja = True
        self.bank = bank
        self.bank_number = bank_number
        self.npwp = npwp
        self.image_url = image_url

def register_pengguna(first_name, last_name, gender, phone_number, birth_date, address):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO ")