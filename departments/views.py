from datetime import datetime
from zoneinfo import ZoneInfo
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView,View, TemplateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

from .forms import DepartmentsForm
from .models import Departments
class ListDepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'view_link':str(reverse_lazy('departments:detail-departments', args=["@@"])),
            'update_link': str(reverse_lazy('departments:update-departments', args=["@@"])),
            'delete_link':str(reverse_lazy('departments:delete-departments', args=["@@"])),
        }

        departments_object = Departments.objects.all()
        departments_data = []

        for dept in departments_object:
            context['hash'] = dept.hash_uuid
            form_action = render_to_string('departments/includes/form_action_button.html', context, request=request)
            
            departments_data.append({
                'name':dept.name,
                'created_at': dept.created_at.date(),
                'status':dept.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'departments_data': departments_data
        }

        return JsonResponse(response)

    def post(self, request):
        pass

class CreateDepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        departments_form = DepartmentsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create departments',
            'departments_form':departments_form,
            'uq':{
                'create_link':str(reverse_lazy('departments:create-departments')),
            }
        }
        
        form = render_to_string('departments/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
            
        }
        return JsonResponse(response)

    def post(self, request):
        print(request.POST)
        departments_form = DepartmentsForm(request.POST or None)

        if departments_form.is_valid():
            print('Departments Form is Valid')
            
            try:
                # Saving User to Database
                departments_data = departments_form.cleaned_data

                # Add Additional Field to Database
                departments_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                departments_data['created_by'] = request.user
                departments_data['updated_at'] = None
                departments_data['updated_by'] = None
                departments_data['deleted_at'] = None
                departments_data['deleted_by'] = None
                
                # Saving Employees to Database
                Departments(**departments_data).save()

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
                'toast_message':'Departments Added Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            messages.error(request,'Please Correct The Errors Below')
            print(messages)
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}

            for field, error_list in departments_form.errors.items():
                errors[field] = error_list
            
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdateDepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, department_uuid):
        department = get_object_or_404(Departments, hash_uuid=department_uuid)

        departments_form = DepartmentsForm(instance=department)

        context = {
            'mode':'update',
            'departments_form':departments_form,
            'modal_title':'update departments',
            'uq':{
                'hash': department_uuid,
                'update_link':str(reverse_lazy('departments:update-departments', args=["@@"])),
            }
        }
        
        form = render_to_string('departments/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
        }

        return JsonResponse(response)

    def post(self, request, department_uuid):
        print(request.POST)
        department = get_object_or_404(Departments, hash_uuid=department_uuid)

        departments_form = DepartmentsForm(request.POST or None, instance=department)

        if departments_form.is_valid():
            print('Form is Valid')
            
            try:
                print('SAVING TO DB')

                # Add Additional Field to Database
                departments_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                departments_form.cleaned_data['updated_by'] = request.user

                # Saving Departments to Database
                departments_form.save()

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
                'toast_message':'Department Updated Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            print('ERRORS')
            print(departments_form.errors)
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}
            for field, error_list in departments_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailDepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, department_uuid):
        department = get_object_or_404(Departments, hash_uuid=department_uuid)

        departments_form = DepartmentsForm(instance=department)

        for key in departments_form.fields:
            departments_form.fields[key].widget.attrs['disabled'] = True
            departments_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'departments_form':departments_form,
            'modal_title':'view departments',
        }
        
        form = render_to_string('departments/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
        }
        return JsonResponse(response)

    def post(self, request):
        pass

class DeleteDepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request, department_uuid):
        
        department = get_object_or_404(Departments, hash_uuid=department_uuid)
        department.status = 0
        department.save()

        response = {
            'success': True, 
            'toast_message':'Department Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class DepartmentsView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def get(self, request):
        context = {
            'title':'Departments',
        }

        return render(request, 'departments/departments.html', context)

    def post(self, request):
        pass