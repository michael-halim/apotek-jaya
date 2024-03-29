# Generated by Django 4.2 on 2023-05-07 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Benefits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='', max_length=200)),
                ('description', models.TextField(default='', max_length=400)),
                ('value', models.IntegerField(default='')),
                ('type_value', models.CharField(default='+', max_length=1)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_benefits', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_benefits', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_benefits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
