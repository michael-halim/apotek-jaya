from django.contrib import admin
from django.utils import timezone
# Register your models here.
from .models import Employees

class EmployeesAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        
        if not change:
            obj.created_by = request.user

        obj.updated_by = request.user
        obj.save()

admin.site.register(Employees,EmployeesAdmin)