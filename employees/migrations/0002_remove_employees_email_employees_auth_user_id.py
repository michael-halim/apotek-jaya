# Generated by Django 4.2 on 2023-04-07 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employees',
            name='email',
        ),
        migrations.AddField(
            model_name='employees',
            name='auth_user_id',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_id_employees', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
