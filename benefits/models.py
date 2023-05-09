from employees.models import Employees
from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import uuid

class Benefits(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    value = models.IntegerField(default='')

    type_value = models.CharField(max_length=1, default='+')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_benefits',
                                      db_column='created_by',
                                      blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_benefits',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='deleted_by_benefits',
                                      db_column='deleted_by',
                                      null=True,
                                      blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'benefits'
        verbose_name_plural = 'Benefits'
        default_permissions = ()
        permissions = (
            ("create_benefits", "Create Benefits"),
            ("read_benefits", "Read Benefits"),
            ("update_benefits", "Update Benefits"),
            ("delete_benefits", "Delete Benefits"),
        )