from django.db import models
from django.contrib.auth.models import User

from employees.models import Employees

import uuid

class Overtimes(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_overtimes',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_overtimes',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_overtimes',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.employee.username
    
    class Meta:
        db_table = 'overtimes'
        verbose_name_plural = 'Overtimes'
        default_permissions = ()
        permissions = (
            ("create_overtimes", "Create Overtimes"),
            ("read_overtimes", "Read Overtimes"),
            ("update_overtimes", "Update Overtimes"),
            ("delete_overtimes", "Delete Overtimes"),
        )

class OvertimeUsers(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    overtime_id = models.ForeignKey(Overtimes,
                                    on_delete=models.CASCADE,
                                    db_column='overtime_id')

    employee_id = models.ForeignKey(Employees,
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')
    

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_overtime_users',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_overtime_users',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_overtime_users',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.employee.username
    
    class Meta:
        db_table = 'overtime_users'
        verbose_name_plural = 'Overtime Users'
        default_permissions = ()
        permissions = (
            ("create_overtime_users", "Create Overtime Users"),
            ("read_overtime_users", "Read Overtime Users"),
            ("update_overtime_users", "Update Overtime Users"),
            ("delete_overtime_users", "Delete Overtime Users"),
        )