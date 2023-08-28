from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .forms import DepartmentMembersForm, DepartmentMembersPermissionGroupForm, DepartmentsForm
from .models import DepartmentMembers, Departments
from employees.models import Employees

from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

class ListDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments']

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
                'created_at': dept.created_at.date().strftime("%d %B %Y"),
                'status':dept.status,
                'uq': form_action, 
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

class AddEmployeeDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments']

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
        employees = request.POST['employees']

        if uuid.UUID(employees, version=4):
            employee = get_object_or_404(Employees, hash_uuid=employees)

            permission_group = request.POST['permission_group']
            if permission_group:
                permission_group = get_object_or_404(Group, id=permission_group)

            nik = employee.nik if employee.nik != '' else '-'
            nik_email = nik + '<br>' + employee.auth_user_id.email
            trash_icon = '''
                <div class="d-flex justify-content-center">
                    <span class="delete-departments-employees btn text-danger w-100">
                        <i class="bi bi-trash"></i>
                    </span>
                </div>
            '''

            employee_data = {
                'uq':employee.hash_uuid,
                'uq_group': permission_group.id if permission_group != '' else '',
                'nik_email':nik_email,
                'name': employee.name,
                'address': employee.address,
                'permission_group':permission_group.name if permission_group != '' else '',
                'education': employee.education,
                'join_date': employee.created_at.date().strftime("%d %B %Y"),
                'expired_at': employee.expired_at.strftime("%d %B %Y"),
                'action':trash_icon,
            }

            response = {
                'success':True,
                'employee_data':employee_data,
            }

            return JsonResponse(response)

        else:
            response = {
                'success':False,
                'toast_message':'Please review the form and correct any errors before resubmitting',
            }

            return JsonResponse(response)

class CreateDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments', 'departments.create_departments']

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
        departments_form = DepartmentsForm()
        department_members_form = DepartmentMembersForm()
        permission_group_form = DepartmentMembersPermissionGroupForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create departments',
            'departments_form':departments_form,
            'department_members_form':department_members_form,
            'permission_group_form':permission_group_form,
            'uq':{
                'create_link':str(reverse_lazy('departments:create-departments')),
            }
        }
        
        form = render_to_string('departments/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        employees = request.POST['employees[]']
        permission_group = request.POST['employees_permission_group[]']

        form_request = request.POST.copy()
        del form_request['employees[]']
        del form_request['employee_id']
        del form_request['group']
        del form_request['employees_permission_group[]']

        if employees != '':
            form_request['employee_id'] = employees.split(',')

            employees = []
            for emp in form_request['employee_id']:
                employees.append(get_object_or_404(Employees, hash_uuid = emp))

        if permission_group != '':
            form_request['group'] = permission_group.split(',')

            permission_group = []
            for group in form_request['group']:
                if group != '' and group.isnumeric():
                    permission_group.append(get_object_or_404(Group, id=group))
                else:
                    permission_group.append('')

        departments_form = DepartmentsForm(form_request or None)
        department_members_form = DepartmentMembersForm(form_request or None)

        if departments_form.is_valid() and department_members_form.is_valid():
            try:
                departments_data = departments_form.cleaned_data
                department_members_data = department_members_form.cleaned_data

                # Add Additional Departments Field to Database
                departments_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                departments_data['created_by'] = request.user
                departments_data['updated_at'] = None
                departments_data['updated_by'] = None
                departments_data['deleted_at'] = None
                departments_data['deleted_by'] = None

                created_department = Departments(**departments_data)
                created_department.save()

                # Add Additional Department Members Field to Database
                department_members_data['department_id'] = created_department
                department_members_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                department_members_data['created_by'] = request.user
                department_members_data['updated_at'] = None
                department_members_data['updated_by'] = None
                
                # Saving Departments and Employees to Database
                for emp, perm_group in zip(employees, permission_group) :
                    department_members_data['employee_id'] = emp
                    DepartmentMembers(**department_members_data).save()
                    
                    if perm_group:
                        emp.auth_user_id.groups.add(perm_group)

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
                'toast_message':'Departments Added Successfuly',
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

class UpdateDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments', 'departments.update_departments']

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
    
    def get(self, request, department_uuid):
        department = get_object_or_404(Departments, hash_uuid=department_uuid)

        department_members_form = DepartmentMembersForm()
        permission_group_form = DepartmentMembersPermissionGroupForm()
        departments_form = DepartmentsForm(instance=department)

        context = {
            'mode':'update',
            'departments_form':departments_form,
            'department_members_form':department_members_form,
            'permission_group_form':permission_group_form,
            'modal_title':'update departments',
            'uq':{
                'hash': department_uuid,
                'update_link':str(reverse_lazy('departments:update-departments', args=["@@"])),
            }
        }
        
        form = render_to_string('departments/includes/form.html', context, request=request)

        department_members = DepartmentMembers.objects.filter(department_id = department.id, status=1)
        trash_icon = '''
                <div class="d-flex justify-content-center">
                    <span class="delete-departments-employees btn text-danger w-100">
                        <i class="bi bi-trash"></i>
                    </span>
                </div>
        '''

        employee_data = []
        for member in department_members:
            nik = member.employee_id.nik if member.employee_id.nik != '' else '-'
            nik_email = nik + '<br>' + member.employee_id.auth_user_id.email
            
            permission_object = member.employee_id.auth_user_id.groups.all()
            permission_group = ''
            group_id = []
            for perm in permission_object:
                permission_group += perm.name + '<br>'
                group_id.append(perm.id)

            employee_data.append({
                'uq':member.employee_id.hash_uuid,
                'uq_group': group_id,
                'nik_email':nik_email,
                'name': member.employee_id.name,
                'address': member.employee_id.address,
                'education': member.employee_id.education,
                'permission_group': permission_group,
                'join_date': member.employee_id.created_at.date().strftime("%d %B %Y"),
                'expired_at': member.employee_id.expired_at.strftime("%d %B %Y"),
                'action':trash_icon,
            })

        response = {
            'success':True,
            'form': form,
            'employee_data':employee_data,
            'is_view_only': False,
        }

        return JsonResponse(response)

    def post(self, request, department_uuid):
        department = get_object_or_404(Departments, hash_uuid=department_uuid)

        employees = request.POST['employees[]']
        employees_permission_group = request.POST['employees_permission_group[]']

        form_request = request.POST.copy()
        del form_request['employees[]']
        del form_request['employees_permission_group[]']

        added_employees, removed_employees, reactivated_employees = [], [], []

        if employees != '':
            # Get Employees Hash
            form_request['employee_id'] = employees.split(',')

            # Get Both Current and Old Employees Hash
            added_employees = [ x for x in form_request['employee_id'] ]
            
            employees_permission_group = employees_permission_group.split(',')
            for emp, perm_group in zip(added_employees,employees_permission_group):
                if not emp or not perm_group:
                    continue

                employee_object = get_object_or_404(Employees, hash_uuid=emp)
                group = get_object_or_404(Group, id=perm_group)
                employee_object.auth_user_id.groups.add(group)

            # Old Employees Remove Employee from Current Employees
            # If the 'try' works, it means employees is reactivated
            department_members = DepartmentMembers.objects.filter(department_id = department.id, status=0)
            old_employees = [ str(x.employee_id.hash_uuid) for x in department_members]
            for old_emp in old_employees:
                try: 
                    added_employees.remove(old_emp)
                    reactivated_employees.append(old_emp)
                except: pass


            # Old Employees Remove Employee from Current Employees
            # If the 'try' works, it means both have the same employees
            # If throws error, it means the old employees is removed
            # The rest is new employee
            department_members = DepartmentMembers.objects.filter(department_id = department.id, status=1)
            old_employees = [ str(x.employee_id.hash_uuid) for x in department_members]
            
            for old_emp in old_employees:
                try: added_employees.remove(old_emp)
                except: removed_employees.append(old_emp)
        
        else:
            # Delete All Members if employees ''
            department_members = DepartmentMembers.objects.filter(department_id = department.id, status=1)
            removed_employees = [ str(x.employee_id.hash_uuid) for x in department_members]



        if isinstance(form_request['employee_id'], str):
            form_request['employee_id'] = [form_request['employee_id']]
            
        departments_form = DepartmentsForm(form_request or None, instance=department)
        department_members_form = DepartmentMembersForm(form_request or None)

        if departments_form.is_valid() and department_members_form.is_valid():
            try:

                # Add Additional Field to Database
                departments_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                departments_form.cleaned_data['updated_by'] = request.user

                # Saving Departments to Database
                departments_form.save()

                department_members_data = department_members_form.cleaned_data
                if added_employees:

                    # Add Additional Department Members Field to Database
                    department_members_data['department_id'] = department
                    department_members_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                    department_members_data['created_by'] = request.user
                    department_members_data['updated_at'] = None
                    department_members_data['updated_by'] = None

                    # Saving Departments and Employees to Database
                    for emp in added_employees:
                        employee = get_object_or_404(Employees, hash_uuid=emp)
                        department_members_data['employee_id'] = employee
                        DepartmentMembers(**department_members_data).save()

                if removed_employees:
                    for emp in removed_employees:
                        employee = get_object_or_404(Employees, hash_uuid=emp)
                        department_members = get_object_or_404(DepartmentMembers, department_id = department, employee_id=employee, status=1)

                        employee.auth_user_id.groups.clear()

                        department_members.status = 0
                        department_members.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        department_members.updated_by = request.user
                        department_members.save()

                if reactivated_employees:
                    for emp in reactivated_employees:
                        employee = get_object_or_404(Employees, hash_uuid=emp)
                        department_members = get_object_or_404(DepartmentMembers, department_id = department, employee_id=employee, status=0)

                        department_members.status = 1
                        department_members.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        department_members.updated_by = request.user
                        department_members.save()

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
                'toast_message':'Department Updated Successfuly',
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

class DetailDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments']

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

        department_members = DepartmentMembers.objects.filter(department_id = department.id, status=1)

        employee_data = []
        for member in department_members:
            nik = member.employee_id.nik if member.employee_id.nik != '' else '-'
            nik_email = nik + '<br>' + member.employee_id.auth_user_id.email

            permission_object = member.employee_id.auth_user_id.groups.all()
            permission_group = ''
            group_id = []
            for perm in permission_object:
                permission_group += perm.name + '<br>'
                group_id.append(perm.id)

            employee_data.append({
                'uq':member.employee_id.hash_uuid,
                'uq_group':group_id,
                'nik_email':nik_email,
                'name': member.employee_id.name,
                'address': member.employee_id.address,
                'education': member.employee_id.education,
                'permission_group': permission_group,
                'join_date': member.employee_id.created_at.date().strftime("%d %B %Y"),
                'expired_at': member.employee_id.expired_at.strftime("%d %B %Y"),
                'action':'',
            })

        response = {
            'success':True,
            'form': form,
            'employee_data':employee_data,
            'is_view_only': True,
        }
        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class DeleteDepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments', 'departments.delete_departments']

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
            return redirect(reverse_lazy('main:home'))

        return redirect(reverse_lazy('main_app:login'))

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

class DepartmentsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['departments.read_departments']

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
            'title':'Departments',
        }

        return render(request, 'departments/departments.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))