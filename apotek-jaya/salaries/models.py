from django.db import models
from django.contrib.auth.models import User

from benefits.models import BenefitAdjustments, BenefitScheme, DetailEmployeeBenefits
from employees.models import Employees
from overtimes.models import OvertimeUsers

import uuid

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

    def __str__(self):
        return self.name
    
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
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    employee_id = models.ForeignKey(Employees, 
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')

    period_id = models.ForeignKey(PayrollPeriods, 
                                    on_delete=models.CASCADE,
                                    db_column='period_id')

    presence_count = models.IntegerField(db_column='presence_count')



    total_work_hours = models.IntegerField(db_column='total_work_hours')

    ptkp = models.IntegerField(db_column='ptkp')

    overtime_hours_count = models.IntegerField(db_column='overtime_hours_count')
    
    overtime_hours_nominal = models.IntegerField(db_column='overtime_hours_nominal')

    leave_count = models.IntegerField(db_column='leave_count')
    
    sick_count = models.IntegerField(db_column='sick_count')
    
    permit_count = models.IntegerField(db_column='permit_count')

    pph21 = models.IntegerField(db_column='pph21')
    
    allowance = models.IntegerField(db_column='allowance')
    
    deduction = models.IntegerField(db_column='deduction')
    
    base_salary = models.IntegerField(db_column='base_salary')
    
    bonus = models.IntegerField(db_column='bonus')

    thr = models.IntegerField(db_column='thr')

    gross_salary = models.IntegerField(db_column='gross_salary')
    
    final_salary = models.IntegerField(db_column='final_salary')

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

    class Meta:
        db_table = 'salaries'
        verbose_name_plural = 'Salaries'
        default_permissions = ()
        permissions = (
            ("create_salaries", "Create Salaries"),
            ("read_salaries", "Read Salaries"),
            ("update_salaries", "Update Salaries"),
            ("delete_salaries", "Delete Salaries"),
        )

class SalaryAdjustments(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200, default='', null=True, blank=True)

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    salary_id = models.ForeignKey(Salaries, 
                                    on_delete=models.CASCADE,
                                    db_column='salary_id')

    value = models.IntegerField(db_column='value')

    is_deduction = models.BooleanField(default=False)

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_salary_adjustments',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_salary_adjustments',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_salary_adjustments',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'salary_adjustments'
        verbose_name_plural = 'Salary Adjustments'
        default_permissions = ()
        permissions = (
            ("create_salary_adjustments", "Create Salary Adjustments"),
            ("read_salary_adjustments", "Read Salary Adjustments"),
            ("update_salary_adjustments", "Update Salary Adjustments"),
            ("delete_salary_adjustments", "Delete Salary Adjustments"),
        )

class SalaryComponents(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=200, default='', null=True, blank=True)

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    salary_id = models.ForeignKey(Salaries, 
                                    on_delete=models.CASCADE,
                                    db_column='salary_id')

    employee_id = models.ForeignKey(Employees,
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')
    
    benefit_scheme_id = models.ForeignKey(BenefitScheme,
                                          on_delete=models.CASCADE,
                                            db_column='benefit_scheme_id',
                                            null=True,
                                            blank=True)                                    

    salary_adjustments_id = models.ForeignKey(SalaryAdjustments,
                                                on_delete=models.CASCADE,
                                                db_column='salary_adjustments_id',
                                                null=True,
                                                blank=True)
    
    benefit_id = models.ForeignKey(DetailEmployeeBenefits,
                                    on_delete=models.CASCADE,
                                    db_column='benefit_id',
                                    null=True,
                                    blank=True)
    
    benefit_adjustments_id = models.ForeignKey(BenefitAdjustments,
                                    on_delete=models.CASCADE,
                                    db_column='benefit_adjustments_id',
                                    null=True,
                                    blank=True)
    
    overtime_id  = models.ForeignKey(OvertimeUsers,
                                    on_delete=models.CASCADE,
                                    db_column='overtime_id',
                                    null=True,
                                    blank=True)

    is_deduction = models.BooleanField(default=False)
    
    is_benefit_adjustment = models.BooleanField(default=False)
    
    is_salary_adjustment = models.BooleanField(default=False)

    is_overtime = models.BooleanField(default=False)

    value = models.IntegerField(db_column='value')
    
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_salaries_components',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_salaries_components',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_salaries_components',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'salary_components'
        verbose_name_plural = 'Salary Components'
        default_permissions = ()
        permissions = (
            ("create_salary_components", "Create Salary Components"),
            ("read_salary_components", "Read Salary Components"),
            ("update_salary_components", "Update Salary Components"),
            ("delete_salary_components", "Delete Salary Components"),
        )