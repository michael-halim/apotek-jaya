from datetime import datetime
from zoneinfo import ZoneInfo
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.models import User, Permission, Group
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from departments.models import DepartmentMembers

from employees.models import Employees
from .forms import PermissionForm, PermissionGroupForm
from .models import AuthGroupExtended, AuthGroupPermissionExtended, AuthUserGroupExtended, AuthUserPermissionExtended


from itertools import chain

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
                
                auth_user_permission_data = {
                    'aup_user_id': user,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'updated_at': None,
                    'updated_by': None,
                    'deleted_at': None,
                    'deleted_by': None,
                }
                for perm in user_perms:
                    auth_user_permission_data['aup_permission_id'] = perm
                    AuthUserPermissionExtended(**auth_user_permission_data).save()
                
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
                    'success': False, 
                    'errors': [], 
                    'modal_messages':[],
                    'toast_message':'Permission Cannot be Empty',
                    'is_close_modal':False,
            }
            if user_perms:
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
    
    #TODO: UPDATE NYA GA PKEK UUID, jadi di url nya bisa @@ karena belum terisi
    def get(self, request, employee_uuid):
        permission_data = []
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        employee_permissions = AuthUserPermissionExtended.objects\
                                    .filter(aup_user_id=employee.auth_user_id.id, status=1)\
                                    .values_list('aup_permission_id', flat=True)
        
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

                deactivated_perms = AuthUserPermissionExtended.objects\
                                        .filter(aup_user_id = user.id, status=0)\
                                        .values_list('aup_permission_id', flat=True)
                
                reactivated_perms = []
                for perm_id in deactivated_perms:
                    try:
                        added_perms.remove(get_object_or_404(Permission, id=perm_id))
                        reactivated_perms.append(get_object_or_404(Permission, id=perm_id))
                    except: pass

                
                old_perms = AuthUserPermissionExtended.objects\
                                        .filter(aup_user_id = user.id, status=1)\
                                        .values_list('aup_permission_id', flat=True)
                
                removed_perms = []
                for perm_id in old_perms:
                    try: added_perms.remove(get_object_or_404(Permission, id=perm_id))
                    except: removed_perms.append(get_object_or_404(Permission, id=perm_id))


                print('added_perms')
                print(added_perms)

                print('removed_perms')
                print(removed_perms)

                print('reactivated_perms')
                print(reactivated_perms)


                if added_perms:
                    user.user_permissions.add(*added_perms)
                    auth_user_permissions_data = {
                        'aup_user_id': user,
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                        'updated_at': None,
                        'updated_by': None,
                        'deleted_at': None,
                        'deleted_by': None,
                    }

                    for perm in added_perms:
                        auth_user_permissions_data['aup_permission_id'] = perm
                        AuthUserPermissionExtended(**auth_user_permissions_data).save()


                if removed_perms:
                    for perm in removed_perms:
                        user_permission = get_object_or_404(AuthUserPermissionExtended, aup_user_id=user.id, aup_permission_id=perm.id)
                        user_permission.status = 0
                        user_permission.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        user_permission.updated_by = request.user
                        user_permission.save()
                

                if reactivated_perms:
                    for perm in reactivated_perms:
                        user_permission = get_object_or_404(AuthUserPermissionExtended, aup_user_id=user.id, aup_permission_id=perm.id)
                        user_permission.status = 1
                        user_permission.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        user_permission.updated_by = request.user
                        user_permission.save()


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
    
    def get(self, request, employee_uuid):
        permission_data = []
        employee = get_object_or_404(Employees, hash_uuid=employee_uuid)
        employee_permissions = AuthUserPermissionExtended.objects\
                                    .filter(aup_user_id=employee.auth_user_id.id, status=1)\
                                    .values_list('aup_permission_id', flat=True)

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
                
                # departments = DepartmentMembers.objects.filter(employee_id=employee.id)
                departments = AuthUserGroupExtended.objects.filter(aug_employee_id=employee.id, status=1)
                department_data = ''
                for dept in departments:
                    department_data += dept.aug_department_id.name + ' -> ' + dept.aug_group_id.name + '<br>'
                
                data = {
                    'uq':employee.hash_uuid,
                    'nik_email':nik_email,
                    'name':employee.name,
                    'department': department_data,
                    'action':form_action,
                }
                
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


class CreatePermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'
    
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
                status = permission_group_form.cleaned_data['status']
                permissions = [ Permission.objects.get(id=p.id) for p in permissions ]
                
                group_object = Group.objects.create(name=group_name)
                auth_group_data = {
                    'auth_group_id': group_object,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'updated_at': None,
                    'updated_by': None,
                    'deleted_at': None,
                    'deleted_by': None,
                    'status': status,
                }

                AuthGroupExtended(**auth_group_data).save()

                group_object.permissions.set(permissions)
                
                auth_group_permissions_data = {
                    'agp_group_id': group_object,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'updated_at': None,
                    'updated_by': None,
                    'deleted_at': None,
                    'deleted_by': None,
                }

                for perm in permissions:
                    auth_group_permissions_data['agp_permission_id'] = perm
                    AuthGroupPermissionExtended(**auth_group_permissions_data).save()


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

class UpdatePermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, group_id):
        group = get_object_or_404(AuthGroupExtended, auth_group_id=group_id)
        
        active_permission_group_ids = AuthGroupPermissionExtended.objects\
                                        .filter(agp_group_id=group_id, status=1)\
                                        .values_list('agp_permission_id', flat=True)
        
        
        initial_data = {
            'group':group.auth_group_id,
            'permissions':active_permission_group_ids,
            'status':group.status
        }

        permission_group_form = PermissionGroupForm(initial=initial_data)

        disabled_field = ['group']

        for field in disabled_field:
            permission_group_form.fields[field].widget.attrs['disabled'] = True
            permission_group_form.fields[field].widget.attrs['placeholder'] = ''

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
                reactivated_perms = []
                group = get_object_or_404(AuthGroupExtended, auth_group_id=group_id)
                
                group.status = permission_group_form.cleaned_data['status']
                group.save()

                permissions = permission_group_form.cleaned_data['permissions']
                added_perms = [ Permission.objects.get(id=p.id) for p in permissions ]

                # Get All Permissions That Are Inactive in a Group
                deactivated_perms = AuthGroupPermissionExtended.objects\
                                            .filter(agp_group_id=group_id, status=0)\
                                            .values_list('agp_permission_id', flat=True)

                # If Deactivated Perms can Remove Added Permissions, It Means the Permissions is Reactivated
                for perm_id in deactivated_perms:
                    try: 
                        added_perms.remove(get_object_or_404(Permission, id=perm_id))
                        reactivated_perms.append(get_object_or_404(Permission, id=perm_id))
                    except: pass
                
                old_perms = AuthGroupPermissionExtended.objects\
                                            .filter(agp_group_id=group_id, status=1)\
                                            .values_list('agp_permission_id', flat=True)

                removed_perms = []
                for perm_id in old_perms:
                    try: added_perms.remove(get_object_or_404(Permission, id=perm_id))
                    except: removed_perms.append(get_object_or_404(Permission, id=perm_id))

                print('added_perms')
                print(added_perms)

                print('removed_perms')
                print(removed_perms)

                print('reactivated_perms')
                print(reactivated_perms)

                if added_perms:
                    group.auth_group_id.permissions.add(*added_perms)

                    auth_group_permissions_data = {
                        'agp_group_id':group.auth_group_id,
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                        'updated_at': None,
                        'updated_by': None,
                        'deleted_at': None,
                        'deleted_by': None,
                    }

                    for perm in added_perms:
                        auth_group_permissions_data['agp_permission_id'] = perm
                        AuthGroupPermissionExtended(**auth_group_permissions_data).save()


                if removed_perms:
                    for perm in removed_perms:
                        permission_group = get_object_or_404(AuthGroupPermissionExtended, agp_group_id=group.id, agp_permission_id=perm.id)
                        permission_group.status = 0
                        permission_group.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        permission_group.updated_by = request.user
                        permission_group.save()


                if reactivated_perms:
                    for perm in reactivated_perms:
                        permission_group = get_object_or_404(AuthGroupPermissionExtended, agp_group_id=group.id, agp_permission_id=perm.id)
                        permission_group.status = 1
                        permission_group.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        permission_group.updated_by = request.user
                        permission_group.save()

                
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

class DetailPermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, group_id):
        group = get_object_or_404(AuthGroupExtended, auth_group_id=group_id)
        permission_group_ids = AuthGroupPermissionExtended.objects\
                                        .filter(agp_group_id=group_id, status=1)\
                                        .values_list('agp_permission_id', flat=True)
        
        initial_data = {
            'group':group.auth_group_id,
            'permissions':permission_group_ids,
            'status':group.status,
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
        pass

class DeletePermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request, group_id):
        print('group_id')
        print(group_id)
        group = get_object_or_404(AuthGroupExtended, auth_group_id=group_id)
        group.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        group.updated_by = request.user
        group.status = 0
        group.save()

        response = {
            'success': True, 
            'toast_message':'Permission Group Deleted Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class ListPermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        print('ENTER PERMISSION GROUP')
        context = {
            'view_link':str(reverse_lazy('permission:detail-permission-group', args=["@@"])),
            'update_link': str(reverse_lazy('permission:update-permission-group', args=["@@"])),
            'delete_link':str(reverse_lazy('permission:delete-permission-group', args=["@@"])),
        }

        
        group_object = AuthGroupExtended.objects.all()
        permission_group_data = []
        for group in group_object:
            context['hash'] = group.auth_group_id.id
            form_action = render_to_string('permission/includes/permission_group_form_action_button.html', context, request=request)
            data = {
                'name':group.auth_group_id.name,
                'created_at':group.created_at.date().strftime("%d %B %Y"),
                'status':group.status,
                'action':form_action,
            }

            permission_group_data.append(data)

        response = {
            'success':True,
            'permission_group_data': permission_group_data
        }

        return JsonResponse(response)

    def post(self, request):
        pass

class PermissionGroupView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'title':'Permission Group'
        }
        return render(request, 'permission/permission_group.html', context)

    def post(self, request):
        pass
