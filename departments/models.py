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