from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .forms import EmployeesForm
from .models import Employees 
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
            nik_email = nik + '<br>' + employee.auth_user_id.email
            employees_data.append({
                'nik_email': nik_email,
                'name':employee.name,
                'address':employee.address,
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
        user_form = CreateUserForm(request.POST or None)
        employees_form = EmployeesForm(request.POST or None)

        if user_form.is_valid() and employees_form.is_valid():
            try:
                # Saving User to Database
                user = user_form.save()

                employees_data = employees_form.cleaned_data

                # Add Additional Field to Database
                employees_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                employees_data['created_by'] = request.user
                employees_data['updated_at'] = None
                employees_data['updated_by'] = None
                employees_data['deleted_at'] = None
                employees_data['deleted_by'] = None
                employees_data['resigned_at'] = None
                employees_data['auth_user_id'] = user
                
                # Saving Data to Database
                Employees(**employees_data).save()

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
            for field, error_list in user_form.errors.items():
                errors[field] = error_list

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
        user = get_object_or_404(User, id=employee.auth_user_id.id)

        user_form = CreateUserForm(instance=user)
        employees_form = EmployeesForm(instance=employee)

        user_form.fields.pop('password1', None)
        user_form.fields.pop('password2', None)

        context = {
            'mode':'update',
            'user_form':user_form,
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
        user = get_object_or_404(User, id=employee.auth_user_id.id)

        employees_form = EmployeesForm(request.POST or None, instance=employee)
        user_form = CreateUserForm(request.POST or None, instance=user, is_updating=True)

        if user_form.is_valid() and employees_form.is_valid():
            try:
                # Saving User to Database
                user_form.save()

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
            for field, error_list in user_form.errors.items():
                errors[field] = error_list

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
        user = get_object_or_404(User, id=employee.auth_user_id.id)

        user_form = CreateUserForm(instance=user)
        employees_form = EmployeesForm(instance=employee)

        user_form.fields.pop('password1', None)
        user_form.fields.pop('password2', None)

        for key in user_form.fields:
            user_form.fields[key].widget.attrs['disabled'] = True
            user_form.fields[key].widget.attrs['placeholder'] = ''

        for key in employees_form.fields:
            employees_form.fields[key].widget.attrs['disabled'] = True
            employees_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'user_form':user_form,
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