from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,View, TemplateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from main_app.forms import CreateUserForm
from .forms import EmployeesForm
from .models import Employees 

from datetime import datetime
from zoneinfo import ZoneInfo

class FetchEmployees(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        employees_object = Employees.objects.all()
        employees_data = []
        for employee in employees_object:
            employees_data.append({
                'nik':employee.nik,
                'name':employee.name,
                'address':employee.address,
                'status':employee.status,
                'created_at': employee.created_at.date(),
                'uq': {
                   'hash': employee.hash_uuid,
                   'update_link': str(reverse_lazy('employees:update-employees', args=["@@"])),
                }, 
                
            })

        response = {
            'employees_data': employees_data
        }

        return JsonResponse(response, safe=False)
    
    def post(self, request):
        pass

class CreateEmployeesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user_form = CreateUserForm()
        employees_form = EmployeesForm()

        context = {
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
            'form': form
            
        }
        return JsonResponse(response)
    
    def post(self, request):
        print(request.POST)
        user_form = CreateUserForm(request.POST or None)
        employees_form = EmployeesForm(request.POST or None)

        if user_form.is_valid() and employees_form.is_valid():
            print('Form is Valid')
            
            try:
                # Saving User to Database
                user = user_form.save()

                employees_data = employees_form.cleaned_data
                # print(employees_data)

                # Add Additional Field to Database
                employees_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                employees_data['created_by'] = request.user
                employees_data['updated_at'] = None
                employees_data['updated_by'] = None
                employees_data['deleted_at'] = None
                employees_data['deleted_by'] = None
                employees_data['resigned_at'] = None
                employees_data['auth_user_id'] = user
                
                # Saving Employees to Database
                Employees(**employees_data).save()

            except Exception as e:
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
        
class UpdateEmployeesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, employee_uuid):
        # TODO: Add Exception if Something Goes Wrong

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
            'form': form
        }
        return JsonResponse(response)

    def post(self, request, employee_uuid):
        print(request.POST)
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        user = get_object_or_404(User, id=employee.auth_user_id.id)

        employees_form = EmployeesForm(request.POST or None, instance=employee)
        user_form = CreateUserForm(request.POST or None, instance=user, is_updating=True)

        print('UPDATED EMPLOYEE FORM')
        print(employees_form)
        print('UPDATED USER FORM')
        print(user_form)
        # employees_form = EmployeesForm(request.POST or None)

        if user_form.is_valid() and employees_form.is_valid():
            print('Form is Valid')
            
            try:
                print('SAVING TO DB')
                # Saving User to Database
                user_form.save()

                # Add Additional Field to Database
                employees_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                employees_form.cleaned_data['updated_by'] = request.user
                
                # Saving Employees to Database
                employees_form.save()

            except Exception as e:
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
                'toast_message':'Employee Updated Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            print('ERRORS')
            print(user_form.errors)
            print(employees_form.errors)
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
        
class EmployeesView(LoginRequiredMixin, View):
    """Handles Employees Page"""

    login_url = '/login/'

    def get(self, request):
        user_form = CreateUserForm()
        employees_form = EmployeesForm()
        # username_context = form.fields['username'].widget.get_context('username', form['username'].value(), form['username'].attrs)['widget']
        print('LOOK HERE')
        print(employees_form.errors)
        print(employees_form.fields['nik'].error_messages)
        print(employees_form.fields['nik'].widget.attrs)
        print(employees_form.fields['nik'].widget.input_type)
        print(employees_form.fields['nik'].label)
        print('BIRTHDATE')
        print(employees_form.fields['birthdate'].widget.format)
        print(employees_form.fields['birthdate'].widget.input_type)
        # print(form.fields['username'].widget.attrs)
        
        print('URL LAZY')
        print(str(reverse_lazy('employees:update-employees', args=["@@"])))
        # employees_form['widget'] = 
        context = {
        }
        return render(request, 'employees/employees.html', context)

    def post(self, request):
        pass