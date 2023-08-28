from django.contrib import admin
from .models import LeaveBalances, Leaves, LeaveRequests 

admin.site.register(Leaves)
admin.site.register(LeaveRequests)
admin.site.register(LeaveBalances)