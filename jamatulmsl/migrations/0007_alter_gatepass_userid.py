# Generated by Django 5.1.2 on 2024-10-24 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jamatulmsl', '0006_rename_vehical_no_gatepass_vehicle_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gatepass',
            name='USERID',
            field=models.CharField(max_length=50),
        ),
    ]
