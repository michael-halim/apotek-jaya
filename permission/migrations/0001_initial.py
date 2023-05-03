# Generated by Django 4.2 on 2023-04-30 12:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroupExtended',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('auth_group_id', models.OneToOneField(db_column='auth_group_id', on_delete=django.db.models.deletion.CASCADE, related_name='auth_group_id', to='auth.group')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_group', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_group', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_group', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Auth Group Extended',
                'db_table': 'auth_group_extended',
                'permissions': (('create_auth_group_extended', 'Create Auth Group Extended'), ('read_auth_group_extended', 'Read Auth Group Extended'), ('update_auth_group_extended', 'Update Auth Group Extended'), ('delete_auth_group_extended', 'Delete Auth Group Extended')),
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='AuthUserPermissionExtended',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('aup_permission_id', models.ForeignKey(db_column='permission_id', on_delete=django.db.models.deletion.CASCADE, related_name='aup_permission_id', to='auth.permission')),
                ('aup_user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='aup_user_id', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_user_permissions', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_user_permissions', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_user_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Auth User Permissions Extended',
                'db_table': 'auth_user_permissions_extended',
                'permissions': (('create_auth_user_permissions_extended', 'Create Auth User Permissions Extended'), ('read_auth_user_permissions_extended', 'Read Auth User Permissions Extended'), ('update_auth_user_permissions_extended', 'Update Auth User Permissions Extended'), ('delete_auth_user_permissions_extended', 'Delete Auth User Permissions Extended')),
                'default_permissions': (),
                'unique_together': {('aup_user_id', 'aup_permission_id')},
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroupExtended',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('aug_group_id', models.ForeignKey(db_column='group_id', on_delete=django.db.models.deletion.CASCADE, related_name='aug_group_id', to='auth.group')),
                ('aug_user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='aug_user_id', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_user_groups', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_user_groups', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_user_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Auth User Group Extended',
                'db_table': 'auth_user_group_extended',
                'permissions': (('create_auth_user_group_extended', 'Create Auth User Group Extended'), ('read_auth_user_group_extended', 'Read Auth User Group Extended'), ('update_auth_user_group_extended', 'Update Auth User Group Extended'), ('delete_auth_user_group_extended', 'Delete Auth User Group Extended')),
                'default_permissions': (),
                'unique_together': {('aug_user_id', 'aug_group_id')},
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissionExtended',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('status', models.IntegerField(default=1)),
                ('agp_group_id', models.ForeignKey(db_column='group_id', on_delete=django.db.models.deletion.CASCADE, related_name='agp_group_id', to='auth.group')),
                ('agp_permission_id', models.ForeignKey(db_column='permission_id', on_delete=django.db.models.deletion.CASCADE, related_name='agp_permission_id', to='auth.permission')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', on_delete=django.db.models.deletion.CASCADE, related_name='created_by_group_permission', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, db_column='deleted_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deleted_by_group_permission', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_by_group_permission', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Auth Group Permission Extended',
                'db_table': 'auth_group_permission_extended',
                'permissions': (('create_auth_group_permission_extended', 'Create Auth Group Permission Extended'), ('read_auth_group_permission_extended', 'Read Auth Group Permission Extended'), ('update_auth_group_permission_extended', 'Update Auth Group Permission Extended'), ('delete_auth_group_permission_extended', 'Delete Auth Group Permission Extended')),
                'default_permissions': (),
                'unique_together': {('agp_group_id', 'agp_permission_id')},
            },
        ),
    ]
