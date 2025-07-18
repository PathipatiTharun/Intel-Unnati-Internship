# Generated by Django 5.2.4 on 2025-07-08 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=100)),
                ('batch_id', models.CharField(max_length=100)),
                ('manufacturing_date', models.DateField()),
                ('rohs_compliance', models.BooleanField(default=False)),
                ('serial_number', models.CharField(max_length=200)),
            ],
        ),
    ]
