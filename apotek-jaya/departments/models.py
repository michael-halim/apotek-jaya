from employees.models import Employees
from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import uuid

class Departments(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default='')
    
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_departments',
                                      db_column='created_by',
                                      blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_departments',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='deleted_by_departments',
                                      db_column='deleted_by',
                                      null=True,
                                      blank=True)

    status = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'departments'
        verbose_name_plural = 'Departments'
        default_permissions = ()
        permissions = (
            ("create_departments", "Create Departments"),
            ("read_departments", "Read Departments"),
            ("update_departments", "Update Departments"),
            ("delete_departments", "Delete Departments"),
        )

class DepartmentMembers(models.Model):
    department_id = models.ForeignKey(Departments, 
                                      on_delete=models.CASCADE,
                                      db_column='department_id')
    
    employee_id = models.ForeignKey(Employees, 
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_department_members',
                                      db_column='created_by',
                                      blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_department_members',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)
    
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'department_members'
        verbose_name_plural = 'Department Members'
        default_permissions = ()
        permissions = (
            ("create_department_members", "Create Department Members"),
            ("read_department_members", "Read Department Members"),
            ("update_department_members", "Update Department Members"),
            ("delete_department_members", "Delete Department Members"),
        )