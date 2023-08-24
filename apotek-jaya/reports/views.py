from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse_lazy

from departments.models import DepartmentMembers, Departments
from salaries.models import PayrollPeriods, Salaries

from zoneinfo import ZoneInfo
import uuid

class ListReportsSalaryView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        period_uuid = request.GET.get('pu', None)
        dept_uuid = request.GET.get('du', None)

        if period_uuid is None and dept_uuid is None:
            response = {
                'success':True,
                'reports_salary_data': []
            }

            return JsonResponse(response)
        
        period_object = PayrollPeriods.objects.all()
        try:
            if uuid.UUID(period_uuid, version=4):
                period_object = PayrollPeriods.objects.filter(hash_uuid=period_uuid)
        except: pass

        dept_object = Departments.objects.all()
        try:
            if uuid.UUID(dept_uuid, version=4):
                dept_object = Departments.objects.filter(hash_uuid=dept_uuid)
        except: pass

        filtered_employees = DepartmentMembers.objects.filter(department_id__in=dept_object)\
                                                        .values_list('employee_id', flat=True)
        
        salaries_object = Salaries.objects.filter(employee_id__in = filtered_employees, period_id__in=period_object)

        reports_data = []
        for salary in salaries_object:
            nik = salary.employee_id.nik if salary.employee_id.nik else '---'
            nik_name = nik + '<br>' + salary.employee_id.name

            department_object = DepartmentMembers.objects.filter(employee_id=salary.employee_id)
            departments_name = [ x.department_id.name for x in department_object ]
            departments_name = ', '.join(departments_name)

            reports_data.append({
                'nik_name': nik_name,
                'department': departments_name,
                'presence_count': salary.presence_count,
                'base_salary': salary.base_salary,
                'allowance': salary.allowance,
                'overtime': salary.overtime_hours_nominal,
                'deduction': salary.deduction,
                'thr': salary.thr,
                'bonus': salary.bonus,
                'gross_salary': salary.gross_salary,
                'final_salary': salary.final_salary,
            })

        response = {
            'success':True,
            'reports_salary_data': reports_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class ReportsSalaryView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'title':'Reports Salary',
        }

        return render(request, 'reports/reports_salary.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class ListReportsPresenceView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        period_uuid = request.GET.get('pu', None)
        dept_uuid = request.GET.get('du', None)

        if period_uuid is None and dept_uuid is None:
            response = {
                'success':True,
                'reports_salary_data': []
            }

            return JsonResponse(response)
        
        period_object = PayrollPeriods.objects.all()
        try:
            if uuid.UUID(period_uuid, version=4):
                period_object = PayrollPeriods.objects.filter(hash_uuid=period_uuid)
        except: pass

        dept_object = Departments.objects.all()
        try:
            if uuid.UUID(dept_uuid, version=4):
                dept_object = Departments.objects.filter(hash_uuid=dept_uuid)
        except: pass

        filtered_employees = DepartmentMembers.objects.filter(department_id__in=dept_object)\
                                                        .values_list('employee_id', flat=True)
        
        salaries_object = Salaries.objects.filter(employee_id__in = filtered_employees, period_id__in=period_object)

        reports_data = []
        for salary in salaries_object:
            nik = salary.employee_id.nik if salary.employee_id.nik else '---'
            nik_name = nik + '<br>' + salary.employee_id.name

            department_object = DepartmentMembers.objects.filter(employee_id=salary.employee_id)
            departments_name = [ x.department_id.name for x in department_object ]
            departments_name = ', '.join(departments_name)

            reports_data.append({
                'nik_name': nik_name,
                'department': departments_name,
                'presence_count': salary.presence_count,
                'total_work_hours': salary.total_work_hours,
                'overtime_hours_count': salary.overtime_hours_count,
                'leave_count': salary.leave_count,
                'sick_count': salary.sick_count,
                'permit_count': salary.permit_count,
            })

        response = {
            'success':True,
            'reports_salary_data': reports_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class ReportsPresenceView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'title':'Reports Salary',
        }

        return render(request, 'reports/reports_presence.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class FetchPeriodsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'toast_message':'You Are Not Authorized',
                'is_close_modal':False,

            }

            return JsonResponse(response)
        
        return redirect(reverse_lazy('main_app:login'))
    
    def get(self, request):
        payroll_period_object = PayrollPeriods.objects.all()
        payroll_periods_data = []

        for pp in payroll_period_object:
            payroll_periods_data.append({
                'hash': pp.hash_uuid,
                'name':pp.name,
                'start_at':pp.start_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%d %B %Y"),
                'end_at':pp.end_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%d %B %Y"),
                'description':pp.description,
            })

        response = {
            'success':True,
            'payroll_periods_data': payroll_periods_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class FetchDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'toast_message':'You Are Not Authorized',
                'is_close_modal':False,

            }

            return JsonResponse(response)
        
        return redirect(reverse_lazy('main_app:login'))
    
    def get(self, request):
        department_object = Departments.objects.all()
        departments_data = []

        for dept in department_object:
            departments_data.append({
                'hash': dept.hash_uuid,
                'name':dept.name,
            })

        response = {
            'success':True,
            'departments_data': departments_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
