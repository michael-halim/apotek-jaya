from django.db import models
from django.contrib.auth.models import User

from employees.models import Employees
from salaries.models import PayrollPeriods

import uuid

class Leaves(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')
    
    description = models.TextField(max_length=400, default='', null=True, blank=True)

    max_duration = models.IntegerField(default=1)

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_leaves',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_leaves',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_leaves',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'leaves'
        verbose_name_plural = 'Leaves'
        default_permissions = ()
        permissions = (
            ("create_leaves", "Create Leave"),
            ("read_leaves", "Read Leave"),
            ("update_leaves", "Update Leave"),
            ("delete_leaves", "Delete Leave"),
        )

class LeaveBalances(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    employee_id = models.ForeignKey(Employees,
                                    on_delete=models.CASCADE, 
                                    db_column='employee_id')
    
    leave_id = models.ForeignKey(Leaves,
                                on_delete=models.CASCADE, 
                                db_column='leave_id')

    balance = models.IntegerField(default=1)

    expired_at = models.DateField()

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_leave_balances',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_leave_balances',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_leave_balances',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.employee.username
    
    class Meta:
        db_table = 'leave_balances'
        verbose_name_plural = 'Leave Balances'
        default_permissions = ()
        permissions = (
            ("create_leave_balances", "Create Leave Balances"),
            ("read_leave_balances", "Read Leave Balances"),
            ("update_leave_balances", "Update Leave Balances"),
            ("delete_leave_balances", "Delete Leave Balances"),
        )

class LeaveRequests(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    period_id = models.ForeignKey(PayrollPeriods,
                                    on_delete=models.CASCADE,
                                    db_column='period_id')
    
    employee_id = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    db_column='employee_id')
    
    leave_type_id = models.ForeignKey(Leaves,
                                    on_delete=models.CASCADE, 
                                    db_column='leave_type_id')
    
    reason = models.TextField(max_length=400, default='', null=True, blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    duration = models.IntegerField(default=1)

    approved_at = models.DateTimeField(null=True, blank=True, default=None)
    approved_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='approved_by_leave_requests',
                                    db_column='approved_by',
                                    blank=True, null=True, default=None)
    
    rejected_at = models.DateTimeField(null=True, blank=True, default=None)
    rejected_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='rejected_by_leave_requests',
                                    db_column='rejected_by',
                                    blank=True, null=True, default=None)
    
    rejected_reason = models.TextField(max_length=400, default='', null=True, blank=True)

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_leave_requests',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_leave_requests',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_leave_requests',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.employee.username
    
    class Meta:
        db_table = 'leave_requests'
        verbose_name_plural = 'Leave Requests'
        default_permissions = ()
        permissions = (
            ("create_leave_requests", "Create Leave Requests"),
            ("read_leave_requests", "Read Leave Requests"),
            ("update_leave_requests", "Update Leave Requests"),
            ("delete_leave_requests", "Delete Leave Requests"),
        )