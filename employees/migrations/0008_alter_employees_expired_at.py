# Generated by Django 4.2 on 2023-05-09 06:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0007_alter_employees_expired_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employees',
            name='expired_at',
            field=models.DateField(default=datetime.date(2024, 5, 8)),
        ),
    ]
