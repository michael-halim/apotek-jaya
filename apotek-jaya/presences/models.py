from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import uuid

from employees.models import Employees

class Presences(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    employee_id = models.ForeignKey(Employees,
                                    on_delete=models.CASCADE,
                                    db_column='employee_id')
    
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()


    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_presences',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_presences',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'presences'
        verbose_name_plural = 'Presences'
        default_permissions = ()
        permissions = (
            ("create_presences", "Create Presence"),
            ("read_presences", "Read Presence"),
            ("update_presences", "Update Presence"),
            ("delete_presences", "Delete Presence"),
        )