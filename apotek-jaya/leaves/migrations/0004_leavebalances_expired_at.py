# Generated by Django 4.2 on 2023-07-25 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaves', '0003_rename_leave_type_id_leavebalances_leave_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavebalances',
            name='expired_at',
            field=models.DateField(default='2023-07-25'),
            preserve_default=False,
        ),
    ]
