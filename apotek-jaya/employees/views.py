from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db.utils import IntegrityError
import openpyxl

from .forms import EmployeesBulkInputForm, EmployeesForm
from .models import Employees 
from benefits.models import PTKPType
from main_app.forms import CreateUserForm

from datetime import datetime
from zoneinfo import ZoneInfo

class ListEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['employees.read_employees']

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
        
    def get(self, request):
        context = {
            'view_link':str(reverse_lazy('employees:detail-employees', args=['@@'])),
            'update_link': str(reverse_lazy('employees:update-employees', args=['@@'])),
            'delete_link':str(reverse_lazy('employees:delete-employees', args=['@@'])),
        }

        employees_object = Employees.objects.all()
        employees_data = []

        for employee in employees_object:
            context['hash'] = employee.hash_uuid
            form_action = render_to_string('employees/includes/form_action_button.html', context, request=request)
            
            nik = employee.nik if employee.nik != '' else '-'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            employees_data.append({
                'nik': nik,
                'name':employee.name,
                'status':employee.status,
                'created_at': employee.created_at.date().strftime("%d %B %Y"),
                'uq': form_action, 
            })

        response = {
            'success':True,
            'employees_data': employees_data
        }

        return JsonResponse(response)
    
    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('employees:employees'))

        return redirect(reverse_lazy('main_app:login'))

class CreateEmployeesView(LoginRequiredMixin, PermissionRequiredMixin ,View):
    login_url = '/login/'
    permission_required = ['employees.read_employees', 'employees.create_employees']

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
        
    def get(self, request):
        user_form = CreateUserForm()
        employees_form = EmployeesForm()
        
        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create employees',
            'user_form':user_form,
            'employees_form':employees_form,
            'uq':{
                'create_link':str(reverse_lazy('employees:create-employees')),
            }
        }
        
        form = render_to_string('employees/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
            
        }
        return JsonResponse(response)
    
    def post(self, request):
        employees_form = EmployeesForm(request.POST or None)

        if employees_form.is_valid():
            try:
                # Saving User to Database
                employees_data = employees_form.cleaned_data

                # Add Additional Field to Database
                employees_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                employees_data['created_by'] = request.user
                employees_data['updated_at'] = None
                employees_data['updated_by'] = None
                employees_data['deleted_at'] = None
                employees_data['deleted_by'] = None
                
                # Saving Data to Database
                Employees(**employees_data).save()

            except Exception as e:
                print('e')
                print(e)
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
                'toast_message':'Employee Added Successfuly',
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
            for field, error_list in employees_form.errors.items():
                errors[field] = error_list
            
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)
        
class UpdateEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['employees.read_employees', 'employees.update_employees']

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

    def get(self, request, employee_uuid):
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        initial_data = {
            'ptkp_type_id':employee.ptkp_type_id
        }

        employees_form = EmployeesForm(instance=employee, initial=initial_data)

        context = {
            'mode':'update',
            'employees_form':employees_form,
            'modal_title':'update employees',
            'uq':{
                'hash': employee_uuid,
                'update_link':str(reverse_lazy('employees:update-employees', args=["@@"])),
            }
        }
        
        form = render_to_string('employees/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
        }

        return JsonResponse(response)

    def post(self, request, employee_uuid):
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        employees_form = EmployeesForm(request.POST or None, instance=employee)
        print('employees_form.is_valid()')
        print(employees_form.is_valid())
        if employees_form.is_valid():
            try:
                # Add Additional Field to Database
                employees_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                employees_form.cleaned_data['updated_by'] = request.user
                
                # Saving Data to Database
                employees_form.save()

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
                'toast_message':'Employee Updated Successfuly',
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
            for field, error_list in employees_form.errors.items():
                errors[field] = error_list
            
            print('errors')
            print(errors)
            print('modal_messages')
            print(modal_messages)
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['employees.read_employees']

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
        
    def get(self, request, employee_uuid):
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        initial_data = {
            'ptkp_type_id':employee.ptkp_type_id
        }
        employees_form = EmployeesForm(instance=employee, initial=initial_data)

        for key in employees_form.fields:
            employees_form.fields[key].widget.attrs['disabled'] = True
            employees_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'employees_form':employees_form,
            'modal_title':'view employees',
        }
        
        form = render_to_string('employees/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
        }
        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('employees:employees'))

        return redirect(reverse_lazy('main_app:login'))

class DeleteEmployeesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['employees.read_employees','employees.delete_employees']

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
    
    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
    def post(self, request, employee_uuid):
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        employee.status = 0
        employee.save()

        response = {
            'success': True, 
            'toast_message':'Employee Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class CreateEmployeesBulkView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['employees.read_employees', 'employees.create_employees']

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
        employees_bulk_form = EmployeesBulkInputForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create employees',
            'employees_bulk_form':employees_bulk_form,
            'uq':{
                'create_link':str(reverse_lazy('employees:create-employees-bulk')),
            }
        }
        
        form = render_to_string('employees/includes/employees_bulk_form.html', context, request=request)
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
            # current_nik = None
            current_line = None
            try:
                workbook = openpyxl.load_workbook(uploaded_file)
                sheet = workbook.active
                
                excel_data = []
                for co, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                    if co == 1:
                        continue
                    nik = row[0]
                    name = row[1]

                    birthdate = None
                    print('row[2]')
                    print(row[2])
                    print(type(row[2]))
                    if isinstance(row[2], str):
                        birthdate = datetime.strptime(row[2], '%d/%m/%Y')
                    elif isinstance(row[2], datetime):
                        birthdate = datetime.strptime(row[2].strftime('%d/%m/%Y'), '%d/%m/%Y')

                    ptkp_type = row[3]

                    print('nik')
                    print(nik)
                    print('name')
                    print(name)
                    print('birthdate')
                    print(birthdate)
                    print(type(birthdate))
                    print('ptkp_type')
                    print(ptkp_type)
               
                    ptkp_type_object = PTKPType.objects.filter(name=ptkp_type)
                    if len(ptkp_type_object) <= 0:
                        failed_response['toast_message'] = 'PTKP Type {ptkp_type} Not Found in line {line}'.format(ptkp_type = ptkp_type, line=co)
                        return JsonResponse(failed_response)
                    
                    excel_data.append({
                        'nik':nik,
                        'name':name,
                        'birthdate':birthdate,
                        'ptkp_type':ptkp_type_object[0],
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                    })

                employees_data = []
                for co, row in enumerate(excel_data, start=1):
                    employees_data.append(Employees(
                        nik=row['nik'],
                        name=row['name'],
                        birthdate=row['birthdate'],
                        ptkp_type_id=row['ptkp_type'],
                        created_at=row['created_at'],
                        created_by=row['created_by'],
                        updated_at=None,
                        updated_by=None,
                        deleted_at=None,
                        deleted_by=None,
                    ))
                
                # Create Bulk Data
                Employees.objects.bulk_create(employees_data)

                response = {
                    'success':True,
                    'toast_message':'Employee Created Successfuly',
                    'is_close_modal': True,
                }

                return JsonResponse(response)
            
            except ValueError as ve:
                response = {
                    'success':False,
                    'errors': [],
                    'toast_message':'There are error in line {line}, error message: {e}'.format(line=current_line, e=ve),
                    'modal_messages':[],
                    'is_close_modal': True,
                }

                return JsonResponse(response)
            
            except Exception as e:
                response = {
                    'success':False,
                    'errors': [],
                    'toast_message':'There are error in line {line}, error message: {e}'.format(line=current_line, e=e),
                    'modal_messages':[],
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

class EmployeesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Handles Employees Page"""

    login_url = '/login/'
    permission_required = ['employees.read_employees']

    def handle_no_permission(self):
        response = {
            'success': False,
            'errors': [],
            'modal_messages':[],
            'toast_message':'You Are Not Authorized',
            'is_close_modal':False,
        }

        return JsonResponse(response)
        
    def get(self, request):
        context = {
            'title':'Employees',
        }

        return render(request, 'employees/employees.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('employees:employees'))

        return redirect(reverse_lazy('main_app:login'))