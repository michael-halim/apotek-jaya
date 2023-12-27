from django.db import models
from django.contrib.auth.models import User

import uuid

class Employees(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default='')
    nik = models.CharField(max_length=20, default='', null=True, blank=True, unique=True)
    birthdate = models.DateField()
    
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.SET_NULL, 
                                      related_name='created_by_employees',
                                      db_column='created_by',
                                      null=True,
                                      blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.SET_NULL, 
                                      related_name='updated_by_employees',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                      on_delete=models.SET_NULL, 
                                      related_name='deleted_by_employees',
                                      db_column='deleted_by',
                                      null=True,
                                      blank=True)

    npwp = models.CharField(max_length=25, default='', null=True, blank=True)
    ptkp_type_id = models.ForeignKey('benefits.PTKPType', 
                                        on_delete=models.SET_NULL,
                                        related_name='ptkp_type_id',
                                        null=True, 
                                        blank=True)

    status = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'employees'
        verbose_name_plural = 'Employees'
        default_permissions = ()
        permissions = (
            ("create_employees", "Create Employees"),
            ("read_employees", "Read Employees"),
            ("update_employees", "Update Employees"),
            ("delete_employees", "Delete Employees"),
        )