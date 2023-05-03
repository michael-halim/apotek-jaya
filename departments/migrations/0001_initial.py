# Generated by Django 4.2 on 2023-04-30 12:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='', max_length=200)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_departments', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_departments', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_departments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Departments',
                'db_table': 'departments',
                'permissions': (('create_departments', 'Create Departments'), ('read_departments', 'Read Departments'), ('update_departments', 'Update Departments'), ('delete_departments', 'Delete Departments')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DepartmentMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_department_members', to=settings.AUTH_USER_MODEL)),
                ('department_id', models.ForeignKey(db_column='department_id', on_delete=django.db.models.deletion.CASCADE, to='departments.departments')),
                ('employee_id', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, to='employees.employees')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_department_members', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Department Members',
                'db_table': 'department_members',
                'permissions': (('create_department_members', 'Create Department Members'), ('read_department_members', 'Read Department Members'), ('update_department_members', 'Update Department Members'), ('delete_department_members', 'Delete Department Members')),
                'default_permissions': (),
            },
        ),
    ]
