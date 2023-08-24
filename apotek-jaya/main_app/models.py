from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UploadFile(models.Model):
    files = models.FileField(upload_to='uploads/')

