# Generated by Django 5.1.2 on 2024-10-23 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jamatulmsl', '0005_rename_vehical_owner_name_gatepass_vehicle_owner_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gatepass',
            old_name='vehical_no',
            new_name='vehicle_no',
        ),
    ]