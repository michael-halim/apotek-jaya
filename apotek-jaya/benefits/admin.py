from django.contrib import admin
from .models import BenefitAdjustments, BenefitCategories, Benefits, BenefitScheme, DetailEmployeeBenefits, PTKPType 

admin.site.register(BenefitAdjustments)
admin.site.register(BenefitCategories)
admin.site.register(Benefits)
admin.site.register(BenefitScheme)
admin.site.register(DetailEmployeeBenefits)
admin.site.register(PTKPType)