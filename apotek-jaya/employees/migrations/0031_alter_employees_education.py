# Generated by Django 4.2 on 2023-12-25 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0030_remove_employees_auth_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employees',
            name='education',
            field=models.CharField(blank=True, default='SD', max_length=10, null=True),
        ),
    ]
