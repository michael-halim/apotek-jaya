from django.db import models

from django.contrib.auth.models import User, Group

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