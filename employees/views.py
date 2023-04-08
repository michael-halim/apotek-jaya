from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View, TemplateView

# Create your views here.
class EmployeesView(LoginRequiredMixin, TemplateView):
    """Handles Employees Page"""

    template_name = 'employees/employees.html'
    login_url = '/login/'