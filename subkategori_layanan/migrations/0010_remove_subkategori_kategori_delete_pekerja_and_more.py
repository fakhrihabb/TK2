# Generated by Django 5.1.3 on 2024-12-01 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subkategori_layanan', '0009_alter_sesilayanan_subkategori_alter_subkategori_tipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subkategori',
            name='kategori',
        ),
        migrations.DeleteModel(
            name='Pekerja',
        ),
        migrations.RemoveField(
            model_name='sesilayanan',
            name='subkategori',
        ),
        migrations.DeleteModel(
            name='Kategori',
        ),
        migrations.DeleteModel(
            name='SesiLayanan',
        ),
        migrations.DeleteModel(
            name='Subkategori',
        ),
    ]
