# Generated by Django 4.2 on 2023-12-26 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0033_alter_employees_nik'),
        ('presences', '0003_alter_presences_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='presences',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='presences',
            name='date',
            field=models.DateField(default='1970-01-01'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='presences',
            unique_together={('employee_id', 'date', 'start_at', 'end_at')},
        ),
    ]
