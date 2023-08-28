from employees.models import Employees
from django.db import models
from django.contrib.auth.models import User

import uuid

class BenefitCategories(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='', unique=True)

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_benefit_category',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_benefit_category',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_benefit_category',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'benefit_categories'
        verbose_name_plural = 'Benefit Categories'
        default_permissions = ()
        permissions = (
            ("create_benefit_categories", "Create Benefit Categories"),
            ("read_benefit_categories", "Read Benefit Categories"),
            ("update_benefit_categories", "Update Benefit Categories"),
            ("delete_benefit_categories", "Delete Benefit Categories"),
        )


class Benefits(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    value = models.IntegerField(default='')

    type_value = models.CharField(max_length=1, default='+')

    benefit_category_id = models.ForeignKey(BenefitCategories,
                                            on_delete=models.CASCADE,
                                            db_column='benefit_category_id')

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


class BenefitScheme(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, default='')

    description = models.TextField(max_length=400, default='', null=True, blank=True)

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_benefit_scheme',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_benefit_scheme',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_benefit_scheme',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'benefit_scheme'
        verbose_name_plural = 'Benefit Schemes'
        default_permissions = ()
        permissions = (
            ("create_benefit_scheme", "Create Benefits Scheme"),
            ("read_benefit_scheme", "Read Benefits Scheme"),
            ("update_benefit_scheme", "Update Benefits Scheme"),
            ("delete_benefit_scheme", "Delete Benefits Scheme"),
        )

class DetailEmployeeBenefits(models.Model):
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    benefit_id = models.ForeignKey(Benefits, 
                                    on_delete=models.CASCADE,
                                    db_column='benefit_id')
    
    benefit_scheme_id = models.ForeignKey(BenefitScheme, 
                                    on_delete=models.CASCADE,
                                    db_column='benefit_scheme_id')
    
    employee_id = models.ForeignKey(Employees, 
                                      on_delete=models.CASCADE,
                                      db_column='employee_id')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_detail_employee_benefits',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_detail_employee_benefits',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_detail_employee_benefits',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return str(self.benefit_id) + ' ' + str(self.benefit_scheme_id) + ' ' + str(self.employee_id)
    
    class Meta:
        unique_together = ('benefit_id', 'benefit_scheme_id', 'employee_id', )
        db_table = 'detail_employee_benefits'
        verbose_name_plural = 'Detail Employee Benefits'
        default_permissions = ()
        permissions = (
            ("create_detail_employee_benefits", "Create Detail Employee Benefits"),
            ("read_detail_employee_benefits", "Read Detail Employee Benefits"),
            ("update_detail_employee_benefits", "Update Detail Employee Benefits"),
            ("delete_detail_employee_benefits", "Delete Detail Employee Benefits"),
        )

class BenefitAdjustments(models.Model):
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    benefit_id = models.ForeignKey(Benefits, 
                                    on_delete=models.CASCADE,
                                    db_column='benefit_id')
    
    benefit_scheme_id = models.ForeignKey(BenefitScheme, 
                                        on_delete=models.CASCADE,
                                        db_column='benefit_scheme_id')

    employee_id = models.ForeignKey(Employees, 
                                      on_delete=models.CASCADE,
                                      db_column='employee_id')
    
    updated_value = models.IntegerField(default='')
    
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_benefit_adjustments',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_benefit_adjustments',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_benefit_adjustments',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return str(self.benefit_id) + ' ' + str(self.benefit_scheme_id) + ' ' + str(self.employee_id)
    
    class Meta:
        unique_together = ('benefit_id', 'benefit_scheme_id', 'employee_id', )
        db_table = 'benefit_adjustments'
        verbose_name_plural = 'Benefit Adjustments'
        default_permissions = ()
        permissions = (
            ("create_benefit_adjustments", "Create Benefit Adjustments"),
            ("read_benefit_adjustments", "Read Benefit Adjustments"),
            ("update_benefit_adjustments", "Update Benefit Adjustments"),
            ("delete_benefit_adjustments", "Delete Benefit Adjustments"),
        )

class PTKPType(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=5, default='')

    value = models.IntegerField(default='')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='created_by_ptkp_type',
                                    db_column='created_by',
                                    blank=True)
    
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='updated_by_ptkp_type',
                                    db_column='updated_by',
                                    null=True, 
                                    blank=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.ForeignKey(User,
                                    on_delete=models.CASCADE, 
                                    related_name='deleted_by_ptkp_type',
                                    db_column='deleted_by',
                                    null=True,
                                    blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'ptkp_type'
        verbose_name_plural = 'PTKP Types'
        default_permissions = ()
        permissions = (
            ("create_ptkp_type", "Create PTKP Type"),
            ("read_ptkp_type", "Read PTKP Type"),
            ("update_ptkp_type", "Update PTKP Type"),
            ("delete_ptkp_type", "Delete PTKP Type"),
        )