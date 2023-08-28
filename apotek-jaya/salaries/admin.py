from django.contrib import admin
from .models import Salaries, SalaryAdjustments, SalaryComponents

admin.site.register(Salaries)
admin.site.register(SalaryAdjustments)
admin.site.register(SalaryComponents)