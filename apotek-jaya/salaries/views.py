from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db import transaction as db_transaction


from .models import PayrollPeriods, Salaries, SalaryAdjustments, SalaryComponents

from benefits.models import BenefitAdjustments, DetailEmployeeBenefits
from departments.models import DepartmentMembers, Departments
from employees.models import Employees
from overtimes.models import OvertimeUsers
from presences.models import Presences
from settings.models import Settings
from salaries.forms import PayrollPeriodBulkInputForm, PayrollPeriodsForm, SalariesForm, SalaryAdjustmentsForm
import openpyxl
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

def calculate_salary(request, employees, period):
    for employee in employees:
        overtime_hours_count, overtime_hours_nominal = 0, 0
        leave_count, sick_count, permit_count = 0, 0, 0
        base_salary, gross_salary, final_salary = 0, 0, 0
        allowance, deduction = 0, 0
        presence_count, total_work_hours = 0, 0
        bonus, thr = 0, 0
        pph21 = 0
        ptkp = employee.ptkp_type_id.value if employee.ptkp_type_id else 54000000

        # Check Employee Benefits and Its Adjustments
        salary_components_data = []
        detail_employee_benefits = DetailEmployeeBenefits.objects.filter(employee_id = employee, status=1)
        for employee_benefit in detail_employee_benefits:
            benefit_adjustments = BenefitAdjustments.objects.filter(benefit_id = employee_benefit.benefit_id,
                                                                    benefit_scheme_id = employee_benefit.benefit_scheme_id,
                                                                    employee_id = employee,
                                                                    status = 1)\
                                                            .first()
            
            current_value = employee_benefit.benefit_id.value
            current_name = employee_benefit.benefit_id.name
            current_description = employee_benefit.benefit_id.description
            is_deduction = True if employee_benefit.benefit_id.type_value == '-' else False
            current_category = employee_benefit.benefit_id.benefit_category_id.name if employee_benefit.benefit_id.benefit_category_id.name else ''


            is_benefit_adjustment = False
            benefit_adjustments_id = None
            benefit_id = employee_benefit
            if benefit_adjustments:
                current_value = benefit_adjustments.updated_value
                is_benefit_adjustment = True
                benefit_adjustments_id = benefit_adjustments
                benefit_id = None

            salary_components_data.append({
                'name': '({current_category}) {current_name}'.format(current_category=current_category, current_name=current_name),
                'description': current_description,
                'value': current_value,
                'employee_id': employee,
                'benefit_scheme_id': employee_benefit.benefit_scheme_id,
                'is_deduction': is_deduction,
                'is_benefit_adjustment': is_benefit_adjustment,
                'benefit_adjustments_id': benefit_adjustments_id,
                'benefit_id': benefit_id,
                'is_overtime': False,
                'overtime_id': None,
                'is_salary_adjustment': False,
                'salary_adjustments_id': None,
                'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                'created_by': request.user,
                'status': 1,
            })

        # Check Employee Overtime
        period_start = period.start_at
        period_start = period_start.astimezone(ZoneInfo('Asia/Bangkok'))
        period_end = period.end_at
        period_end = period_end.astimezone(ZoneInfo('Asia/Bangkok'))

        company_settings = Settings.objects.first()
        overtime_rate = company_settings.overtime_rate
        lembur_rate = company_settings.lembur_rate

        overtime_object = OvertimeUsers.objects.filter(employee_id = employee, status=1)
        for ovt in overtime_object:
            if ovt.overtime_id.start_at >= period_start and ovt.overtime_id.end_at <= period_end:
                duration = ovt.overtime_id.end_at - ovt.overtime_id.start_at
                duration_hours = duration.seconds / 3600 if int(duration.seconds / 3600) > 0 else 0
                duration_minutes = (duration.seconds % 3600) / 60

                # is_overtime true = overtime, false = lembur
                is_overtime = ovt.overtime_id.is_overtime
                ovt_value = lembur_rate
                ovt_name = 'Lembur'
                if is_overtime:
                    ovt_value = overtime_rate
                    ovt_name = 'Overtime'

                salary_components_data.append({
                    'name': '({name} Hours) '.format(name=ovt_name) + ovt.overtime_id.name,
                    'description': '',
                    'value': duration_hours * ovt_value,
                    'employee_id': employee,
                    'benefit_scheme_id': None,
                    'is_deduction': False,
                    'is_benefit_adjustment': False,
                    'benefit_adjustments_id': None,
                    'benefit_id': None,
                    'is_overtime': True,
                    'overtime_id': ovt,
                    'is_salary_adjustment': False,
                    'salary_adjustments_id': None,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'status': 1,
                })

                overtime_hours_nominal += duration_hours * ovt_value
                overtime_hours_count += duration_hours
        
        # Check Employee Presence
        presence_object = Presences.objects.filter(employee_id = employee, 
                                                   start_at__gt=period_start, 
                                                   end_at__lte=period_end,
                                                   status=1)
        
        presence_count = presence_object.count()
        for presence in presence_object:
            duration = presence.end_at - presence.start_at
            duration = duration.seconds / 3600 if int(duration.seconds / 3600) > 0 else 0
            total_work_hours += duration

        value = total_work_hours * 0
        salary_components_data.append({
            'name': '(Presence) ' + str(presence_count) + ' Days Worked',
            'description': 'Total Work Hours: ' + str(round(total_work_hours, 2)),
            'value': value,
            'employee_id': employee,
            'benefit_scheme_id': None,
            'is_deduction': False,
            'is_benefit_adjustment': False,
            'salary_adjustments_id': None,
            'benefit_id': None,
            'is_overtime': False,
            'overtime_id': None,
            'is_salary_adjustment': False,
            'benefit_adjustments_id': None,
            'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
            'created_by': request.user,
            'status': 1,
        })
        
        # Check If Salary Already Exist, It Might Have Salary Adjustments
        salary_object = Salaries.objects.filter(employee_id = employee, status=1, period_id=period).first()

        if salary_object:
            salary_adjustments_object = SalaryAdjustments.objects.filter(salary_id=salary_object, status = 1)
            for salary_adjustment in salary_adjustments_object:
                salary_components_data.append({
                    'name': salary_adjustment.name,
                    'description': salary_adjustment.description,
                    'value': salary_adjustment.value,
                    'employee_id': salary_adjustment.salary_id.employee_id,
                    'benefit_scheme_id': None,
                    'is_deduction': salary_adjustment.is_deduction,
                    'is_benefit_adjustment': False,
                    'is_salary_adjustment': True,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'salary_adjustments_id': salary_adjustment,
                    'benefit_id': None,
                    'benefit_adjustments_id': None,
                    'status': 1,
                })
        
        # Calculate Salary Based on Benefit and Its Adjustments and Salary Adjustments
        for sc_data in salary_components_data:
            name = sc_data['name'].lower() if sc_data['name'] else ''
            if 'gaji pokok' in name:
                base_salary += sc_data['value']

            elif 'tunjangan' in name:
                allowance += sc_data['value']
                
            elif 'bonus' in name:
                bonus += sc_data['value']

            elif 'potongan' in name:
                deduction += sc_data['value']
            
            elif 'thr' in name:
                thr += sc_data['value']

            if sc_data['is_deduction']:
                gross_salary -= sc_data['value']
            else:
                gross_salary += sc_data['value']
            
        
        # Calculate PPH21
        # PKP Tax Bracket
        # 0 - 60jt      -> 5%
        # 60jt - 250jt  -> 15%
        # 250jt - 500jt -> 25%
        # 500jt - 5M    -> 30%
        # >5M           -> 35%
        tax_bracket = {
            '60000000': 0.05,
            '250000000': 0.15, 
            '500000000': 0.25,
            '5000000000': 0.3,
            '>5000000000':0.35,
        }

        tmp_gross_salary = (gross_salary * 12) - ptkp
        if tmp_gross_salary > 0:
            for t in tax_bracket:
                if t == '>5000000000':
                    pph21 += tmp_gross_salary * tax_bracket[t]
                    break

                elif tmp_gross_salary - int(t) < 0:
                    pph21 += tmp_gross_salary * tax_bracket[t]
                    break
                
                pph21 += int(t) * tax_bracket[t]
                tmp_gross_salary -= int(t)

            pph21 /= 12
            final_salary = gross_salary - pph21

        else:
            final_salary = gross_salary

        salaries_data = {
            'presence_count': presence_count,
            'total_work_hours': total_work_hours,
            'ptkp': ptkp,
            'overtime_hours_count': overtime_hours_count,
            'overtime_hours_nominal': overtime_hours_nominal,
            'leave_count': leave_count,
            'sick_count': sick_count,
            'permit_count': permit_count,
            'pph21': pph21,
            'employee_id': employee,
            'base_salary': base_salary,
            'allowance': allowance,
            'deduction': deduction,
            'bonus': bonus,
            'thr': thr,
            'gross_salary': gross_salary,
            'final_salary': final_salary,
            'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
            'created_by': request.user,
            'period_id': period,
            'status': 1,
        }

        # If Salary Already Exist, Update It, Else Create New One
        if salary_object:
            del salaries_data['created_at']
            del salaries_data['created_by']
            salaries_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
            salaries_data['updated_by'] = request.user

            for key, value in salaries_data.items():
                setattr(salary_object, key, value)

        else:
            salary_object = Salaries(**salaries_data)
        
        salary_object.save()

        # If Salary Components Already Exist, Update It, Else Create New One
        salary_components_object = SalaryComponents.objects.filter(employee_id=employee, salary_id=salary_object, status=1)
        if salary_components_object:
            # Sometimes, Latest Salary Components Is Not Yet Saved To Database, So We Need To Insert It Later
            added_salary_components = salary_components_data.copy()
            for sc_object, sc_data in zip(salary_components_object, salary_components_data):
                for key, value in sc_data.items():
                    setattr(sc_object, key, value)

                added_salary_components.remove(sc_data)
                sc_object.salary_id = salary_object
                sc_object.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                sc_object.updated_by = request.user
                sc_object.save()

            for sc_data in added_salary_components:
                sc_data['salary_id'] = salary_object
                SalaryComponents(**sc_data).save()

        else:
            for sc_data in salary_components_data:
                sc_data['salary_id'] = salary_object
                SalaryComponents(**sc_data).save()


class ListSalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
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
        period_uuid = request.GET.get('pu', None)
        dept_uuid = request.GET.get('du', None)

        if period_uuid is None and dept_uuid is None:
            response = {
                'success':True,
                'salaries_data': []
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

        context = {
            'view_link':str(reverse_lazy('salaries:detail-salaries', args=["@@"])),
            'update_link': str(reverse_lazy('salaries:update-salaries', args=["@@"])),
            'delete_link':str(reverse_lazy('salaries:delete-salaries', args=["@@"])),
        }

        filtered_employees = DepartmentMembers.objects.filter(department_id__in=dept_object)\
                                                        .values_list('employee_id', flat=True)
        
        salaries_object = Salaries.objects.filter(employee_id__in = filtered_employees, period_id__in=period_object)
        salaries_data = []

        for salary in salaries_object:
            context['hash'] = salary.hash_uuid
            form_action = render_to_string('salaries/includes/salaries_form_action_button.html', context, request=request)
            
            nik = salary.employee_id.nik if salary.employee_id.nik else '---'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            nik_name = nik + '<br>' + salary.employee_id.name
            department_object = DepartmentMembers.objects.filter(employee_id = salary.employee_id)

            departments_name = [ x.department_id.name for x in department_object ]
            departments_name = ', '.join(departments_name)

            salaries_data.append({
                'nik_name': nik_name,
                'department': departments_name,
                'gross_salary': str(salary.gross_salary),
                'final_salary': str(salary.final_salary),
                'created_at': salary.period_id.name,
                'status': salary.status,
                'uq': form_action,
            })

        response = {
            'success':True,
            'salaries_data': salaries_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    

class CalculateSalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries','salaries.create_salaries']

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
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request):
        period_message = 'All Periods'
        payroll_periods = PayrollPeriods.objects.all()
        try:
            if uuid.UUID(request.POST['period_uuid'], version=4):
                payroll_periods = PayrollPeriods.objects.filter(hash_uuid=request.POST['period_uuid'])
                period_message = payroll_periods[0].name

        except: pass
        
        dept_message = 'All Departments'
        dept_object = Departments.objects.all()
        try:
            if uuid.UUID(request.POST['dept_uuid'], version=4):
                dept_object = Departments.objects.filter(hash_uuid=request.POST['dept_uuid'])
                dept_message = dept_object[0].name

        except: pass
        filtered_employees = DepartmentMembers.objects.filter(department_id__in=dept_object)\
                                                        .distinct('employee_id')
        
        employees = [ x.employee_id for x in filtered_employees ]

        for period in payroll_periods:
            calculate_salary(request, employees=employees, period=period)

        response = {
            'success': True,
            'toast_message': 'Successfuly Generated Salaries for ' + dept_message + ' in ' + period_message,
        }
        
        return JsonResponse(response)

class UpdateSalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries','salaries.update_salaries']

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
    
    def get(self, request, salary_uuid):
        salary_object = get_object_or_404(Salaries, hash_uuid=salary_uuid)
        initial_data = {
            'employee_id':salary_object.employee_id,
            'period_id':salary_object.period_id,
        }

        salaries_form = SalariesForm(instance=salary_object, initial=initial_data)
        salary_adjustments_form = SalaryAdjustmentsForm()

        for key in salaries_form.fields:
            salaries_form.fields[key].widget.attrs['disabled'] = True

        context = {
            'mode':'update',
            'salaries_form':salaries_form,
            'salary_adjustments_form':salary_adjustments_form,
            'modal_title':'update salaries',
            'uq':{
                'hash': salary_uuid,
                'update_link':str(reverse_lazy('salaries:update-salaries', args=["@@"])),
            }
        }
        
        form = render_to_string('salaries/includes/salaries_form.html', context, request=request)

        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-salary-components btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''
        salary_components_data = []
        salary_components_object = SalaryComponents.objects.filter(salary_id = salary_object, status=1)
        for sc in salary_components_object:
            type_value = '-' if sc.is_deduction else '+'
            benefit_scheme_name = sc.benefit_scheme_id.name if sc.benefit_scheme_id else '-'
            salary_components_data.append({
                'uq_benefit': sc.hash_uuid,
                'name': sc.name,
                'description': sc.description,
                'type_value': type_value,
                'benefit_scheme' : benefit_scheme_name,
                'is_benefit_adjustment' : sc.is_benefit_adjustment,
                'value': sc.value,
                'action': trash_icon,
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
            'salary_components_data': salary_components_data,
        }

        return JsonResponse(response)

    def post(self, request, salary_uuid):
        # Check Salary Component and Adjustment Validity
        added_salary_components, removed_salary_components = [], []
        if len(request.POST['salary_components[]']) > 0:
            for comp in request.POST['salary_components[]'].split(','):
                try:
                    if uuid.UUID(comp, version=4):
                        added_salary_components.append(comp)

                except ValueError as ve:
                    response = {
                        'success': False, 
                        'errors': [], 
                        'modal_messages':[],
                        'toast_message':'Invalid Salary Components UUID',
                        'is_close_modal':False,
                    }

                    return JsonResponse(response)
            
        salary = get_object_or_404(Salaries, hash_uuid=salary_uuid)
        salary.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        salary.updated_by = request.user

        active_salary_components = SalaryComponents.objects.filter(salary_id=salary.id, status=1)\
                                                            .values_list('hash_uuid', flat=True)
        
        for comp in active_salary_components:
            try: added_salary_components.remove(str(comp))
            except ValueError as ve: removed_salary_components.append(str(comp))

        try:
            # Saving Salary to Database
            salary.save()
            
            if removed_salary_components:
                for salary_comp_uuid in removed_salary_components:
                    salary_component = get_object_or_404(SalaryComponents, hash_uuid=salary_comp_uuid)
                    salary_component.status = 0
                    salary_component.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                    salary_component.deleted_by = request.user
                    salary_component.save()
                
                    if salary_component.is_salary_adjustment:
                        salary_adjustment = get_object_or_404(SalaryAdjustments, id=salary_component.salary_adjustments_id.id)
                        salary_adjustment.status = 0
                        salary_adjustment.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        salary_adjustment.deleted_by = request.user
                        salary_adjustment.save()

                    elif salary_component.is_overtime:
                        overtime = get_object_or_404(OvertimeUsers, id=salary_component.overtime_id.id)
                        overtime.status = 0
                        overtime.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        overtime.deleted_by = request.user
                        overtime.save()

                    elif salary_component.is_benefit_adjustment:
                        benefit_adjustment = get_object_or_404(BenefitAdjustments, id=salary_component.benefit_adjustments_id.id)
                        benefit_adjustment.status = 0
                        benefit_adjustment.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        benefit_adjustment.deleted_by = request.user
                        benefit_adjustment.save()

                    else:
                        benefit = get_object_or_404(DetailEmployeeBenefits, id=salary_component.benefit_id.id)
                        benefit.status = 0
                        benefit.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        benefit.deleted_by = request.user
                        benefit.save()

            calculate_salary(request, employees=Employees.objects.filter(id=salary.employee_id.id), period=salary.period_id)
            
        except Exception as e:
            response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'toast_message':'We\'re sorry, but something went wrong on our end. Please try again later.',
                'is_close_modal':False,
            }

            return JsonResponse(response)
        
        response = {
            'success': True, 
            'toast_message':'Salary Updated and Recalculated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

  
class DetailSalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
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
    
    def get(self, request, salary_uuid):
        salary_object = get_object_or_404(Salaries, hash_uuid=salary_uuid)
        
        initial_data = {
            'employee_id':salary_object.employee_id,
            'period_id':salary_object.period_id
        }

        salaries_form = SalariesForm(instance=salary_object, initial=initial_data)

        for key in salaries_form.fields:
            salaries_form.fields[key].widget.attrs['disabled'] = True
            salaries_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'salaries_form':salaries_form,
            'modal_title':'view salaries',
        }
        
        form = render_to_string('salaries/includes/salaries_form.html', context, request=request)

        salary_components_data = []
        salary_components_object = SalaryComponents.objects.filter(salary_id = salary_object)
        for sc in salary_components_object:
            type_value = '-' if sc.is_deduction else '+'
            benefit_scheme_name = sc.benefit_scheme_id.name if sc.benefit_scheme_id else '-'
            salary_components_data.append({
                'uq_benefit': sc.hash_uuid,
                'name': sc.name,
                'description': sc.description,
                'type_value': type_value,
                'benefit_scheme' : benefit_scheme_name,
                'is_benefit_adjustment': sc.is_benefit_adjustment,
                'value': sc.value,
                'action': '',
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
            'salary_components_data': salary_components_data,
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class DeleteSalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries','salaries.delete_salaries']

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
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request, salary_uuid):
        salary = get_object_or_404(Salaries, hash_uuid=salary_uuid)
        salary.status = 0
        salary.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        salary.deleted_by = request.user
        salary.save()

        response = {
            'success': True, 
            'toast_message':'Salary Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class SalariesView(LoginRequiredMixin, PermissionRequiredMixin, View):
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
        context = {
            'title':'Salaries',
        }

        return render(request, 'salaries/salaries.html', context)

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
        

class AddSalaryAdjustmentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_salaries', 'salaries.update_salaries', 'salaries.create_salary_adjustments']

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
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request):
        uuid_invalid = True
        try: 
            if uuid.UUID(request.POST['salary_uuid'], version=4): 
                uuid_invalid = False
        except ValueError as ve: uuid_invalid = True
            
        if uuid_invalid:
            response = {
                'success': False, 
                'errors': [], 
                'modal_messages':[],
                'toast_message':'Invalid Salary UUID',
                'is_close_modal':False,
            }
            return JsonResponse(response)
        
        salary_request = request.POST.copy()
        salary_request['salary_id'] = get_object_or_404(Salaries, hash_uuid=request.POST['salary_uuid'])

        salary_adjustments_form = SalaryAdjustmentsForm(salary_request or None)

        if salary_adjustments_form.is_valid():
            
            saved_salary_adjustment = None
            salary_components_data = []
            try:
                salary_adjustments_data = salary_adjustments_form.cleaned_data
                salary_object = get_object_or_404(Salaries, hash_uuid=request.POST['salary_uuid'])

                # Add Additional Benefits Field to Database
                salary_adjustments_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                salary_adjustments_data['created_by'] = request.user
                salary_adjustments_data['updated_at'] = None
                salary_adjustments_data['updated_by'] = None
                salary_adjustments_data['deleted_at'] = None
                salary_adjustments_data['deleted_by'] = None
                salary_adjustments_data['salary_id'] = salary_object

                saved_salary_adjustment = SalaryAdjustments(**salary_adjustments_data)
                saved_salary_adjustment.save()
                
                trash_icon = '''
                    <div class='d-flex justify-content-center'>
                        <span class='delete-salary-components btn text-danger w-100'>
                            <i class="bi bi-trash"></i>
                        </span>
                    </div>
                '''

                type_value = '-' if saved_salary_adjustment.is_deduction else '+'
                salary_components_data = [{
                    'uq_benefit': saved_salary_adjustment.hash_uuid,
                    'name': saved_salary_adjustment.name,
                    'description': saved_salary_adjustment.description,
                    'type_value': type_value,
                    'benefit_scheme' : '-',
                    'is_benefit_adjustment' : False,
                    'value': saved_salary_adjustment.value,
                    'action': trash_icon,

                }]

            except Exception as e:
                response = {
                    'success': False, 
                    'errors': [], 
                    'modal_messages':[],
                    'toast_message':'We\'re sorry, but something went wrong on our end. Please try again later.',
                    'is_close_modal':False,
                }

                return JsonResponse(response)


            response = {
                'success': True, 
                'toast_message':'Salary Adjustment Added Successfuly',
                'is_close_modal':False,
                'salary_components_data': salary_components_data,
            }

            return JsonResponse(response)

        else:
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}

            for field, error_list in salary_adjustments_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class ListPayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
        context = {
            'view_link':str(reverse_lazy('salaries:detail-payroll-periods', args=["@@"])),
            'update_link': str(reverse_lazy('salaries:update-payroll-periods', args=["@@"])),
            'delete_link':str(reverse_lazy('salaries:delete-payroll-periods', args=["@@"])),
        }

        payroll_period_object = PayrollPeriods.objects.all()
        payroll_periods_data = []

        for pp in payroll_period_object:
            context['hash'] = pp.hash_uuid
            form_action = render_to_string('salaries/includes/payroll_periods_form_action_button.html', context, request=request)
            
            payroll_periods_data.append({
                'name':pp.name,
                'description':pp.description,
                'start_at': pp.start_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'end_at': pp.end_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'status': pp.status,
                'uq': form_action, 
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


class CreatePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.create_payroll_period']

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
        payroll_periods_form = PayrollPeriodsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create payroll period',
            'payroll_periods_form':payroll_periods_form,
            'uq':{
                'create_link':str(reverse_lazy('salaries:create-payroll-periods')),
            }
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        payroll_periods_form = PayrollPeriodsForm(request.POST or None)

        if payroll_periods_form.is_valid():
            try:
                payroll_period_data = payroll_periods_form.cleaned_data

                # Add Additional Benefits Field to Database
                payroll_period_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                payroll_period_data['created_by'] = request.user
                payroll_period_data['updated_at'] = None
                payroll_period_data['updated_by'] = None
                payroll_period_data['deleted_at'] = None
                payroll_period_data['deleted_by'] = None

                PayrollPeriods(**payroll_period_data).save()

            except Exception as e:
                response = {
                    'success': False, 
                    'errors': [], 
                    'modal_messages':[],
                    'toast_message':'We\'re sorry, but something went wrong on our end. Please try again later.',
                    'is_close_modal':False,
                }

                return JsonResponse(response)
            
            response = {
                'success': True, 
                'toast_message':'Payroll Period Added Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}

            for field, error_list in payroll_periods_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class UpdatePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.update_payroll_period']

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
    
    def get(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)

        payroll_periods_form = PayrollPeriodsForm(instance=payroll_period)

        context = {
            'mode':'update',
            'payroll_periods_form':payroll_periods_form,
            'modal_title':'update payroll period',
            'uq':{
                'hash': period_uuid,
                'update_link':str(reverse_lazy('salaries:update-payroll-periods', args=["@@"])),
            }
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
        }

        return JsonResponse(response)

    def post(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)
        payroll_period_form = PayrollPeriodsForm(request.POST or None, instance=payroll_period)

        if payroll_period_form.is_valid():
            
            try:

                # Add Additional Field to Database
                payroll_period_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                payroll_period_form.cleaned_data['updated_by'] = request.user
                
                # Saving Payroll Period to Database
                payroll_period_form.save()

            except Exception as e:
                response = {
                    'success': False,
                    'errors': [],
                    'modal_messages':[],
                    'toast_message':'We\'re sorry, but something went wrong on our end. Please try again later.',
                    'is_close_modal':False,
                }

                return JsonResponse(response)
            
            response = {
                'success': True, 
                'toast_message':'Payroll Period Updated Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}
            for field, error_list in payroll_period_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class DetailPayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
    
    def get(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)

        payroll_periods_form = PayrollPeriodsForm(instance=payroll_period)

        for key in payroll_periods_form.fields:
            payroll_periods_form.fields[key].widget.attrs['disabled'] = True
            payroll_periods_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'payroll_periods_form':payroll_periods_form,
            'modal_title':'view payroll period',
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class DeletePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.delete_payroll_period']

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
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)
        payroll_period.status = 0
        payroll_period.save()

        response = {
            'success': True, 
            'toast_message':'Payroll Period Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class CreatePayrollPeriodBulkView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.create_payroll_period']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'toast_message':'You Are Not Authorized',
                'is_close_modal':True,

            }

            return JsonResponse(response)
        
        return redirect(reverse_lazy('main_app:login'))
    
    def get(self, request):
        payroll_period_bulk_form = PayrollPeriodBulkInputForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create payroll period',
            'payroll_period_bulk_form':payroll_period_bulk_form,
            'uq':{
                'create_link':str(reverse_lazy('salaries:create-payroll-periods-bulk')),
            }
        }
        
        form = render_to_string('salaries/includes/payroll_periods_bulk_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        
        return JsonResponse(response)

    def post(self, request):
        if request.method == 'POST' and request.FILES['file_upload']:
            failed_response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'is_close_modal':False,
            }

            uploaded_file = request.FILES['file_upload']
            if not uploaded_file.name.endswith('.xlsx') and not uploaded_file.name.endswith('.xls'):
                failed_response['toast_message'] = 'File Must Be in .xlsx or .xls Format'
                return JsonResponse(failed_response)
            
            # Add Current NIK and Line in Excel Code for Error Message
            current_line = None
            try:
                workbook = openpyxl.load_workbook(uploaded_file)
                sheet = workbook.active
                
                excel_data = []
                dates = []
                for co, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                    if co == 1 or (row[0] is None and row[1] is None and row[2] is None and row[3] is None):
                        continue
                    
                    start_at = row[2]
                    end_at = row[3]
                    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
                        try:
                            start_at = datetime.strptime(str(start_at), fmt).date()
                            break
                        except ValueError: pass
                    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
                        try:
                            end_at = datetime.strptime(str(end_at), fmt).date()
                            break
                        except ValueError: pass
                    name = row[0]
                    description = row[1]
                    
                    if start_at is None or end_at is None:
                        failed_response['toast_message'] = 'Date in line {line} is not valid'.format(line=co)
                        return JsonResponse(failed_response)
                    
                    excel_data.append({
                        'name':name,
                        'description': description,
                        'start_at': start_at,
                        'end_at': end_at,
                    })

                payroll_period_data = []
                for co, row in enumerate(excel_data, start=1):
                    payroll_period_data.append(PayrollPeriods(
                        name=row['name'],
                        description=row['description'],
                        start_at=row['start_at'],
                        end_at=row['end_at'],
                        status=1,
                        created_at=datetime.now(ZoneInfo('Asia/Bangkok')),
                        created_by=request.user,
                        updated_at=None,
                        updated_by=None,
                        deleted_at=None,
                        deleted_by=None,
                    ))
                
                # Create Bulk Data
                with db_transaction.atomic():
                    PayrollPeriods.objects.bulk_create(payroll_period_data)

                response = {
                    'success':True,
                    'toast_message':'Payroll Periods Created Successfuly',
                    'is_close_modal': True,
                }

                return JsonResponse(response)
            
            except ValueError as ve:
                print('ve')
                print(ve)
                response = {
                    'success':False,
                    'toast_message':'There are error in line {line}'.format(line=current_line),
                    'is_close_modal': True,
                }

                return JsonResponse(response)
        
        failed_response = {
            'success': False,
            'errors': [],
            'toast_message': 'File Upload Failed',
            'modal_messages':[],
            'is_close_modal':False,
        }

        return JsonResponse(failed_response)

class PayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
        context = {
            'title':'Payroll Period',
        }

        return render(request, 'salaries/payroll_periods.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))