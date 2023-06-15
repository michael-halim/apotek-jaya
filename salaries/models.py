from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import uuid

from employees.models import Employees

class PayrollPeriods(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_payroll_period',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_payroll_period',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_payroll_period',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'payroll_period'
        verbose_name_plural = 'Payroll Period'
        default_permissions = ()
        permissions = (
            ("create_payroll_period", "Create Payroll Period"),
            ("read_payroll_period", "Read Payroll Period"),
            ("update_payroll_period", "Update Payroll Period"),
            ("delete_payroll_period", "Delete Payroll Period"),
        )

class Salaries(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    # TODO: APAKAH PERLU DICOPAS KAN SEMUA BENEFIT NYA ?
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    employee_id = models.ForeignKey(Employees, 
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')

    period_id = models.ForeignKey(PayrollPeriods, 
                                    on_delete=models.CASCADE,
                                    db_column='period_id')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_salaries',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_salaries',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_salaries',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)