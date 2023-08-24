from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.models import User, Permission, Group
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from departments.models import DepartmentMembers

from .forms import PermissionForm, PermissionGroupForm
from employees.models import Employees

class CreatePermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_permission', 'auth.add_permission']

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
        permission_form = PermissionForm(is_creating=True)
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
        permission_form = PermissionForm(request.POST or None)

        if permission_form.is_valid():
            try:
                employees = permission_form.cleaned_data['employees']
                user = get_object_or_404(User, id=employees.auth_user_id.id)

                permissions = permission_form.cleaned_data['permissions']
                user_perms = [ Permission.objects.get(id=p.id) for p in permissions ]
                
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
    permission_required = ['auth.view_permission', 'auth.change_permission']

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

    def get(self, request, employee_uuid):
        permission_data = []
        employee = Employees.objects.filter(hash_uuid=employee_uuid)[0]
        employee_permissions = employee.auth_user_id.user_permissions.all()
        employee_permissions = [ x.id for x in employee_permissions ]
        
        initial_data = {
            'employees':[ employee.id ],
            'permissions':employee_permissions,
        }

        permission_form = PermissionForm(initial=initial_data)

        context = {
            'mode':'update',
            'permission_form':permission_form,
            'modal_title':'update permission',
            'uq':{
                'hash':employee_uuid,
                'update_link':str(reverse_lazy('permission:update-permission', args=["@@"])),
            }
        }
        
        form = render_to_string('permission/includes/form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'permission_data':permission_data,
            'is_view_only': True,
        }

        return JsonResponse(response)

    def post(self, request, employee_uuid):
        print(request.POST)
        print('employee_uuid')
        print(employee_uuid)

        permission_form = PermissionForm(request.POST or None, is_updating=True)

        if permission_form.is_valid():
            print('Permission Form is Valid')
            try:
                print('saving to DB')
                employees = permission_form.cleaned_data['employees']
                user = get_object_or_404(User, id=employees.auth_user_id.id)

                permissions = permission_form.cleaned_data['permissions']
                added_perms = [ Permission.objects.get(id=p.id) for p in permissions ]

                old_perms = user.user_permissions.all()
                
                removed_perms = []

                for p in old_perms:
                    try: added_perms.remove(p)
                    except: removed_perms.append(p)

                if added_perms:
                    user.user_permissions.add(*added_perms)

                if removed_perms:
                    user.user_permissions.remove(*removed_perms)
                
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

class DetailPermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_permission']

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
        permission_data = []
        employee = Employees.objects.filter(hash_uuid=employee_uuid)[0]
        employee_permissions = employee.auth_user_id.user_permissions.all()
        employee_permissions = [ x.id for x in employee_permissions ]
        
        initial_data = {
            'employees':[ employee.id ],
            'permissions':employee_permissions,
        }

        permission_form = PermissionForm(initial=initial_data)

        for key in permission_form.fields:
            permission_form.fields[key].widget.attrs['disabled'] = True
            permission_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'permission_form':permission_form,
            'modal_title':'view permission',
        }
        
        form = render_to_string('permission/includes/form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'permission_data':permission_data,
            'is_view_only': True,
        }
        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class DeletePermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_permission', 'auth.delete_permission']

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

    def post(self, request, employee_uuid):
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        
        employee.auth_user_id.user_permissions.clear()

        response = {
            'success': True, 
            'toast_message':'Permission Deleted Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)
    
class ListPermissionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_permission']

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
        print('ENTER PERMISSION')
        context = {
            'view_link':str(reverse_lazy('permission:detail-permission', args=["@@"])),
            'update_link': str(reverse_lazy('permission:update-permission', args=["@@"])),
            'delete_link':str(reverse_lazy('permission:delete-permission', args=["@@"])),
        }

        user_object = User.objects.filter(is_superuser=False)
        permission_data = []
        for user in user_object:
            employee = Employees.objects.filter(auth_user_id=user.id)
            permission_object = user.user_permissions.all()

            if len(permission_object) >= 1 and len(employee) >= 1:
                employee = employee[0]
                
                context['hash'] = employee.hash_uuid
                form_action = render_to_string('permission/includes/form_action_button.html', context, request=request)

                group_object = user.groups.all()

                nik = employee.nik if employee.nik != '' else '-'
                nik_email = nik + '<br>' + employee.auth_user_id.email
                
                departments = DepartmentMembers.objects.filter(employee_id=employee.id)
                departments_data = ''
                for dept in departments:
                    departments_data += dept.department_id.name + '<br>'
                
                data = {
                    'uq':employee.hash_uuid,
                    'nik_email':nik_email,
                    'name':employee.name,
                    'department': departments_data,
                    'action':form_action,
                }
                
                group_names = ''
                for group in group_object:
                    group_names += group.name + '<br>'
                
                data['group_name'] = group_names

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
    permission_required = ['auth.view_permission']

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
            'title':'Permission'
        }
        return render(request, 'permission/permission.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class CreatePermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth_view_group' ,'auth.add_group']

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
        permission_group_form = PermissionGroupForm()
        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create permission group',
            'permission_group_form':permission_group_form,
            'uq':{
                'create_link':str(reverse_lazy('permission:create-permission-group')),
            }
        }
        
        form = render_to_string('permission/includes/permission_group_form.html', context, request=request)
        response = {
            'success':True,
            'form': form
            
        }
        return JsonResponse(response)

    def post(self, request):
        print(request.POST)
        permission_group_form = PermissionGroupForm(request.POST or None)

        if permission_group_form.is_valid():
            try:
                group_name = permission_group_form.cleaned_data['group']
                
                permissions = permission_group_form.cleaned_data['permissions']
                permissions = [ Permission.objects.get(id=p.id) for p in permissions ]
                
                group_object = Group.objects.create(name=group_name)
                group_object.permissions.set(permissions)
                
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
                'toast_message':'Permission Group Added Successfuly',
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
            for field, error_list in permission_group_form.errors.items():
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

class UpdatePermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_group' ,'auth.change_group']

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
    
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        group_permissions = group.permissions.all().values_list('id', flat=True)
        
        initial_data = {
            'group':group,
            'permissions':group_permissions,
            'status': group.status
        }

        permission_group_form = PermissionGroupForm(initial=initial_data)

        permission_group_form.fields['group'].widget.attrs['disabled'] = True
        permission_group_form.fields['group'].widget.attrs['placeholder'] = ''


        context = {
            'mode':'update',
            'permission_group_form':permission_group_form,
            'modal_title':'update permission group',
            'uq':{
                'hash':group_id,
                'update_link':str(reverse_lazy('permission:update-permission-group', args=["@@"])),
            }
        }
        
        form = render_to_string('permission/includes/permission_group_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }
        return JsonResponse(response)

    def post(self, request, group_id):
        print(request.POST)

        permission_group_form = PermissionGroupForm(request.POST or None, is_updating=True)

        if permission_group_form.is_valid():
            print('Permission Group Form is Valid')
            try:
                print('saving to DB')
                group = get_object_or_404(Group, id=group_id)
                permissions = permission_group_form.cleaned_data['permissions']

                added_perms = [ Permission.objects.get(id=p.id) for p in permissions ]

                old_perms = group.permissions.all()
                
                removed_perms = []

                for p in old_perms:
                    try: added_perms.remove(p)
                    except: removed_perms.append(p)

                if added_perms:
                    group.permissions.add(*added_perms)

                if removed_perms:
                    group.permissions.remove(*removed_perms)
                
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
                'toast_message':'Permission Group Added Successfuly',
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
            for field, error_list in permission_group_form.errors.items():
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

class DetailPermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_group']

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
    
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        group_permissions = group.permissions.all().values_list('id', flat=True)
        
        initial_data = {
            'group':group,
            'permissions':group_permissions,
        }

        permission_group_form = PermissionGroupForm(initial=initial_data)

        for key in permission_group_form.fields:
            permission_group_form.fields[key].widget.attrs['disabled'] = True
            permission_group_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'permission_group_form':permission_group_form,
            'modal_title':'view permission group',
        }
        
        form = render_to_string('permission/includes/permission_group_form.html', context, request=request)

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

class DeletePermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_group', 'auth.delete_group']

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

    def post(self, request, group_id):
        print('ENTER DELETE PERMISSION GROUP')
        group = get_object_or_404(Group, id=group_id)
        group.delete()

        response = {
            'success': True, 
            'toast_message':'Permission Group Deleted Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class ListPermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_group']

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
        print('ENTER PERMISSION GROUP')
        context = {
            'view_link':str(reverse_lazy('permission:detail-permission-group', args=["@@"])),
            'update_link': str(reverse_lazy('permission:update-permission-group', args=["@@"])),
            'delete_link':str(reverse_lazy('permission:delete-permission-group', args=["@@"])),
        }

        group_object = Group.objects.all()
        permission_group_data = []
        for group in group_object:
            context['hash'] = group.id
            form_action = render_to_string('permission/includes/permission_group_form_action_button.html', context, request=request)
            data = {
                'name':group.name,
                'action':form_action,
            }

            permission_group_data.append(data)

        response = {
            'success':True,
            'permission_group_data': permission_group_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class PermissionGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['auth.view_group']

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
            'title':'Permission Group'
        }
        return render(request, 'permission/permission_group.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
