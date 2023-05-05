from django.db import models

# Create your models here.
from django.contrib.auth.models import User, Permission, Group

from departments.models import Departments
from employees.models import Employees

class AuthGroupExtended(models.Model):
    auth_group_id = models.OneToOneField(Group, 
                                     on_delete=models.CASCADE,
                                     related_name='auth_group_id',
                                     db_column='auth_group_id')

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='created_by_group',
                                      db_column='created_by',
                                      blank=True)

    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    updated_by = models.ForeignKey(User,
                                      on_delete=models.CASCADE, 
                                      related_name='updated_by_group',
                                      db_column='updated_by',
                                      null=True, 
                                      blank=True)

    status = models.IntegerField(default=1)

    def __str__(self):
        return str(self.auth_group_id.name)

    class Meta:
        db_table = 'auth_group_extended'
        verbose_name_plural = 'Auth Group Extended'
        default_permissions = ()
        permissions = (
            ("create_auth_group_extended", "Create Auth Group Extended"),
            ("read_auth_group_extended", "Read Auth Group Extended"),
            ("update_auth_group_extended", "Update Auth Group Extended"),
            ("delete_auth_group_extended", "Delete Auth Group Extended"),
        )

# class AuthGroupPermissionExtended(models.Model):
#     agp_group_id = models.ForeignKey(Group, 
#                                 on_delete=models.CASCADE,
#                                 related_name='agp_group_id',
#                                 db_column='group_id')

#     agp_permission_id = models.ForeignKey(Permission, 
#                                       on_delete=models.CASCADE,
#                                       related_name='agp_permission_id',
#                                       db_column='permission_id')

#     created_at = models.DateTimeField()
#     created_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='created_by_group_permission',
#                                       db_column='created_by',
#                                       blank=True)

#     updated_at = models.DateTimeField(null=True, blank=True, default=None)
#     updated_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='updated_by_group_permission',
#                                       db_column='updated_by',
#                                       null=True, 
#                                       blank=True)

#     deleted_at = models.DateTimeField(null=True, blank=True, default=None)
#     deleted_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='deleted_by_group_permission',
#                                       db_column='deleted_by',
#                                       null=True,
#                                       blank=True)

#     status = models.IntegerField(default=1)


#     def __str__(self):
#         return str(self.agp_group_id) + ' ' + str(self.agp_permission_id)

#     class Meta:
#         unique_together = ('agp_group_id', 'agp_permission_id')
#         db_table = 'auth_group_permission_extended'
#         verbose_name_plural = 'Auth Group Permission Extended'
#         default_permissions = ()
#         permissions = (
#             ("create_auth_group_permission_extended", "Create Auth Group Permission Extended"),
#             ("read_auth_group_permission_extended", "Read Auth Group Permission Extended"),
#             ("update_auth_group_permission_extended", "Update Auth Group Permission Extended"),
#             ("delete_auth_group_permission_extended", "Delete Auth Group Permission Extended"),
#         )

# class AuthUserGroupExtended(models.Model):
#     aug_employee_id = models.ForeignKey(Employees, 
#                                 on_delete=models.CASCADE,
#                                 related_name='aug_employee_id',
#                                 db_column='employee_id')

#     aug_group_id = models.ForeignKey(Group, 
#                                 on_delete=models.CASCADE,
#                                 related_name='aug_group_id',
#                                 db_column='group_id')

#     aug_department_id = models.ForeignKey(Departments, 
#                                 on_delete=models.CASCADE,
#                                 related_name='aug_department_id',
#                                 db_column='department_id')


#     created_at = models.DateTimeField()
#     created_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='created_by_user_groups',
#                                       db_column='created_by',
#                                       blank=True)

#     updated_at = models.DateTimeField(null=True, blank=True, default=None)
#     updated_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='updated_by_user_groups',
#                                       db_column='updated_by',
#                                       null=True, 
#                                       blank=True)

#     deleted_at = models.DateTimeField(null=True, blank=True, default=None)
#     deleted_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='deleted_by_user_groups',
#                                       db_column='deleted_by',
#                                       null=True,
#                                       blank=True)

#     status = models.IntegerField(default=1)


#     def __str__(self):
#         return str(self.aug_employee_id) + ' ' + str(self.aug_group_id) + ' ' + str(self.aug_department_id)


#     class Meta:
#         unique_together = ('aug_employee_id', 'aug_group_id', 'aug_department_id')
#         db_table = 'auth_user_group_extended'
#         verbose_name_plural = 'Auth User Group Extended'
#         default_permissions = ()
#         permissions = (
#             ("create_auth_user_group_extended", "Create Auth User Group Extended"),
#             ("read_auth_user_group_extended", "Read Auth User Group Extended"),
#             ("update_auth_user_group_extended", "Update Auth User Group Extended"),
#             ("delete_auth_user_group_extended", "Delete Auth User Group Extended"),
#         )


# class AuthUserPermissionExtended(models.Model):
#     aup_user_id = models.ForeignKey(User, 
#                                 on_delete=models.CASCADE,
#                                 related_name='aup_user_id',
#                                 db_column='user_id')

#     aup_permission_id = models.ForeignKey(Permission, 
#                                       on_delete=models.CASCADE,
#                                       related_name='aup_permission_id',
#                                       db_column='permission_id')

#     created_at = models.DateTimeField()
#     created_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='created_by_user_permissions',
#                                       db_column='created_by',
#                                       blank=True)

#     updated_at = models.DateTimeField(null=True, blank=True, default=None)
#     updated_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='updated_by_user_permissions',
#                                       db_column='updated_by',
#                                       null=True, 
#                                       blank=True)

#     deleted_at = models.DateTimeField(null=True, blank=True, default=None)
#     deleted_by = models.ForeignKey(User,
#                                       on_delete=models.CASCADE, 
#                                       related_name='deleted_by_user_permissions',
#                                       db_column='deleted_by',
#                                       null=True,
#                                       blank=True)

#     status = models.IntegerField(default=1)

#     def __str__(self):
#         return self.auth_user_permissions_id

#     class Meta:
#         unique_together = ('aup_user_id', 'aup_permission_id')
#         db_table = 'auth_user_permissions_extended'
#         verbose_name_plural = 'Auth User Permissions Extended'
#         default_permissions = ()
#         permissions = (
#             ("create_auth_user_permissions_extended", "Create Auth User Permissions Extended"),
#             ("read_auth_user_permissions_extended", "Read Auth User Permissions Extended"),
#             ("update_auth_user_permissions_extended", "Update Auth User Permissions Extended"),
#             ("delete_auth_user_permissions_extended", "Delete Auth User Permissions Extended"),
#         )