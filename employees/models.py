from django.db import models
from django.contrib.auth.models import User

from .constants import PROVINCE

class Employees(models.Model):
    auth_user_id = models.OneToOneField(User, 
                                     on_delete=models.CASCADE,
                                     related_name='user_id_employees',
                                     db_column='auth_user_id')
    
    nik = models.CharField(max_length=20, default='', null=True, blank=True)
    birthdate = models.DateField()
    birthplace = models.CharField(max_length=200, default='', null=True , blank=True)
    bloodtype = models.CharField(max_length=5, default='', null=True, blank=True)
    address = models.CharField(max_length=400, default='', null=True, blank=True)
    rt = models.CharField(max_length=4, default='00')
    rw = models.CharField(max_length=4, default='00')
    province = models.CharField(max_length=100, choices=PROVINCE)
    domicile = models.CharField(max_length=400, default='', null=True, blank=True)
    phone = models.CharField(max_length=20, default='', null=True, blank=True)
    join_date = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField()
    created_by = models.OneToOneField(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_employees',
                                      db_column='created_by',
                                      blank=True)

    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.OneToOneField(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_employees',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)

    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.OneToOneField(User,
                                      on_delete=models.CASCADE, 
                                      related_name='deleted_by_employees',
                                      db_column='deleted_by',
                                      null=True,
                                      blank=True)

    expired_at = models.DateTimeField(null=True, blank=True, default=None)
    npwp = models.CharField(max_length=25, default='', null=True, blank=True)
    education = models.CharField(max_length=10, default='SD', null=True)
    resigned_at = models.DateTimeField(null=True, blank=True, default=None)
    status = models.IntegerField(default=1)
    
    def __str__(self):
        return self.auth_user_id.username
    
    class Meta:
        db_table = 'employees'
        verbose_name_plural = 'Employees'