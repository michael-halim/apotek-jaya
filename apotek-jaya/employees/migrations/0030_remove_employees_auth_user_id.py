# Generated by Django 4.2 on 2023-12-25 05:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0029_alter_employees_birthplace_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employees',
            name='auth_user_id',
        ),
    ]
