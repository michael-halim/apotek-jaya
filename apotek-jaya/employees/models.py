from django.db import models
from django.contrib.auth.models import User
from .constants import PROVINCE

from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
import uuid
# TODO:
# BUAT WEBSITE INI BISA DIAKSES OFFLINE
class Employees(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    auth_user_id = models.OneToOneField(User, 
                                     on_delete=models.CASCADE,
                                     related_name='user_id_employees',
                                     db_column='auth_user_id')
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default='')
    nik = models.CharField(max_length=20, default='', null=True, blank=True)
    birthdate = models.DateField()
    birthplace = models.CharField(max_length=200)
    bloodtype = models.CharField(max_length=5, default='', null=True, blank=True)
    address = models.CharField(max_length=400, default='', null=True, blank=True)
    rt = models.CharField(max_length=4, default='00')
    rw = models.CharField(max_length=4, default='00')
    province = models.CharField(max_length=100, choices=PROVINCE)
    domicile = models.CharField(max_length=400, default='', null=True, blank=True)
    phone = models.CharField(max_length=20, default='', null=True, blank=True)
    gender = models.CharField(max_length=5, choices=(('L', 'Laki - Laki'), ('P', 'Perempuan')))
    
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_employees',
                                      db_column='created_by',
                                      blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_employees',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='deleted_by_employees',
                                      db_column='deleted_by',
                                      null=True,
                                      blank=True)

    expired_at = models.DateField(default=datetime.now(ZoneInfo('Asia/Bangkok')).date() + timedelta(days=365))
    npwp = models.CharField(max_length=25, default='', null=True, blank=True)
    education = models.CharField(max_length=10, default='SD', null=True)
    resigned_at = models.DateTimeField(null=True, blank=True, default=None)
    ptkp_type_id = models.ForeignKey('benefits.PTKPType', 
                                        on_delete=models.CASCADE,
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