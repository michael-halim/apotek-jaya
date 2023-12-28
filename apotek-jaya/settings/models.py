from django.db import models

import uuid

class Settings(models.Model):
    # If null=True, in forms is allowed to enter None, if not validators will come into play
    hash_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    overtime_rate = models.IntegerField(default=0, null=True, blank=True)
    lembur_rate = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'settings'
        verbose_name_plural = 'Settings'
        default_permissions = ()
        permissions = (
            ("create_settings", "Create Settings"),
            ("read_settings", "Read Settings"),
            ("update_settings", "Update Settings"),
        )