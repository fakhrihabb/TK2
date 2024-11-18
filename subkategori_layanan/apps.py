from django.apps import AppConfig


class SubkategoriLayananConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subkategori_layanan'

    def ready(self):
        from .views import load_dummy_data
        from django.http import HttpRequest

        request = HttpRequest()
        try:
            load_dummy_data(request)
            print("Dummy data loaded successfully.")
        except Exception as e:
            print(f"Error loading dummy data: {e}")