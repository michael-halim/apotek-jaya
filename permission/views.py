from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView,View, TemplateView
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from employees.models import Employees

from .forms import PermissionForm
class CreatePermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.add_permission']

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
        permission_form = PermissionForm()
        print(permission_form)
        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create permission',
            'permission_form':permission_form,
            'uq':{
                'create_link':str(reverse_lazy('permission:create-permission')),
            }
        }
        
        form = render_to_string('permission/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form
            
        }
        return JsonResponse(response)
    
    def post(self, request):
        print(request.POST)
        permission_form = PermissionForm(request.POST)

        if permission_form.is_valid():
            try:
                user = permission_form.cleaned_data['user']
                print('User')
                print(user)
                print(user.id)
                user = get_object_or_404(User, id=user.id)
                permissions = permission_form.cleaned_data['permissions']
                user_perms = [ Permission.objects.get(id=p.id) for p in permissions ]
                print('user perms')
                print(user_perms)
                
                user.user_permissions.set(user_perms)
                
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
                'toast_message':'Permission Added Successfuly',
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
            for field, error_list in permission_form.errors.items():
                errors[field] = error_list

            print('form not valid')
            print(errors)
            print(modal_messages)
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)
class UpdatePermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.change_permission']

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
        pass

    def post(self, request):
        pass

class DetailPermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.view_permission']

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
        pass

    def post(self, request):
        pass

class DeletePermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.delete_permission']

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
        pass

    def post(self, request):
        pass
class ListPermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.view_permission']

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
        print('ENTER PERMISSION')
        context = {
            'view_link':str(reverse_lazy('employees:detail-employees', args=["@@"])),
            'update_link': str(reverse_lazy('employees:update-employees', args=["@@"])),
            'delete_link':str(reverse_lazy('employees:delete-employees', args=["@@"])),
        }
        form_action = render_to_string('permission/includes/form_action_button.html', context, request=request)

        user_object = User.objects.all()
        permission_data = []
        for user in user_object:
            employee = Employees.objects.filter(auth_user_id=user)
            if len(employee) >= 1:
                employee = employee[0]

                group_object = user.groups.all()
                permission_object = user.user_permissions.all()
                data = {
                    'nik':employee.nik,
                    'name':employee.name,
                    'department':'Departemen',
                    'uq':form_action,
                }

                for group in group_object:
                    data['group_name'] = group.name
                
                for perm in permission_object:
                    data['permission'] = perm.name

                permission_data.append(data)

        response = {
            'success':True,
            'permission_data': permission_data
        }

        return JsonResponse(response)
    
    def post(self, request):
        pass

class PermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['permission.view_permission']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))
        
        return redirect(reverse_lazy('main_app:login'))

    def get(self, request):
        context = {
            'title':'Permission'
        }
        return render(request, 'permission/permission.html', context)

    def post(self, request):
        pass