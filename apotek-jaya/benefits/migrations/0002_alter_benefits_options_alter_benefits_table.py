# Generated by Django 4.2 on 2023-05-07 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benefits', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='benefits',
            options={'default_permissions': (), 'permissions': (('create_benefits', 'Create Benefits'), ('read_benefits', 'Read Benefits'), ('update_benefits', 'Update Benefits'), ('delete_benefits', 'Delete Benefits')), 'verbose_name_plural': 'Benefits'},
        ),
        migrations.AlterModelTable(
            name='benefits',
            table='benefits',
        ),
    ]
