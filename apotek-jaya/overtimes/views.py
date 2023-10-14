from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .forms import OvertimeUsersForm, OvertimesForm
from .models import OvertimeUsers, Overtimes
from departments.models import DepartmentMembers
from employees.models import Employees

from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

class ListOvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes']

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
            'view_link':str(reverse_lazy('overtimes:detail-overtimes', args=["@@"])),
            'update_link': str(reverse_lazy('overtimes:update-overtimes', args=["@@"])),
            'delete_link':str(reverse_lazy('overtimes:delete-overtimes', args=["@@"])),
        }

        overtimes_object = Overtimes.objects.all()
        overtimes_data = []

        for overtime in overtimes_object:
            context['hash'] = overtime.hash_uuid
            form_action = render_to_string('overtimes/includes/overtimes_form_action_button.html', context, request=request)
            
            overtimes_data.append({
                'name':overtime.name,
                'description':overtime.description,
                'start_at':overtime.start_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%d %B %Y %H:%M"),
                'end_at':overtime.end_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%d %B %Y %H:%M"),
                'created_at': overtime.created_at.date().strftime("%d %B %Y"),
                'status':overtime.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'overtimes_data': overtimes_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class CreateOvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes', 'overtimes.create_overtimes']

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
        overtimes_form = OvertimesForm()
        overtime_users_form = OvertimeUsersForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create overtimes',
            'overtimes_form':overtimes_form,
            'overtime_users_form':overtime_users_form,
            'uq':{
                'create_link':str(reverse_lazy('overtimes:create-overtimes')),
            }
        }
        
        form = render_to_string('overtimes/includes/overtimes_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }
        
        return JsonResponse(response)

    def post(self, request):
        overtime_users = []
        for ovt_user in request.POST['overtime_users[]'].split(','):
            try:
                if uuid.UUID(ovt_user, version=4):
                    overtime_users.append(get_object_or_404(Employees, hash_uuid=ovt_user))

            except ValueError as ve:
                response = {
                    'success': False, 
                    'errors': [], 
                    'modal_messages':[],
                    'toast_message':'Invalid Employee UUID',
                    'is_close_modal':False,
                }

                return JsonResponse(response)
            
        overtimes_form = OvertimesForm(request.POST or None)

        if overtimes_form.is_valid():
            try:
                overtime_data = overtimes_form.cleaned_data

                # Add Additional Field to Database
                overtime_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                overtime_data['created_by'] = request.user
                overtime_data['updated_at'] = None
                overtime_data['updated_by'] = None
                overtime_data['deleted_at'] = None
                overtime_data['deleted_by'] = None

                overtime = Overtimes(**overtime_data)
                overtime.save()

                overtime_users_data = {
                    'overtime_id': overtime,
                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                    'created_by': request.user,
                    'updated_at': None,
                    'updated_by': None,
                    'deleted_at': None,
                    'deleted_by': None,
                }

                for ovt_user in overtime_users:
                    overtime_users_data['employee_id'] = ovt_user
                    OvertimeUsers(**overtime_users_data).save()

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
                'toast_message':'Overtime Added Successfuly',
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

            for field, error_list in overtimes_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdateOvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes', 'overtimes.update_overtimes']

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
    
    def get(self, request, overtime_uuid):
        overtimes_object = get_object_or_404(Overtimes, hash_uuid=overtime_uuid)
        overtimes_form = OvertimesForm(instance=overtimes_object)
        overtime_users_form = OvertimeUsersForm()

        context = {
            'mode':'update',
            'overtimes_form':overtimes_form,
            'overtime_users_form':overtime_users_form,
            'modal_title':'update overtimes',
            'uq':{
                'hash': overtime_uuid,
                'update_link':str(reverse_lazy('overtimes:update-overtimes', args=["@@"])),
            }
        }
        
        form = render_to_string('overtimes/includes/overtimes_form.html', context, request=request)

        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-overtime-users btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        overtime_users_data = []
        overtime_users_object = OvertimeUsers.objects.filter(overtime_id = overtimes_object, status=1)
        for ou in overtime_users_object:
            nik = ou.employee_id.nik if ou.employee_id.nik else '-'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            nik_name = nik + '<br>' + ou.employee_id.name
            department_members_object = DepartmentMembers.objects.filter(employee_id=ou.employee_id.id, status=1)
            departments = [ x.department_id.name for x in department_members_object ]
            overtime_users_data.append({
                'uq_employee': ou.employee_id.hash_uuid,
                'nik_name': nik_name,
                'departments': departments,
                'status' : ou.status,
                'action': trash_icon,
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            'overtime_users_data': overtime_users_data,
        }

        return JsonResponse(response)

    def post(self, request, overtime_uuid):
        overtimes = get_object_or_404(Overtimes, hash_uuid=overtime_uuid)
        overtimes_form = OvertimesForm(request.POST or None, instance=overtimes)
        
        now = datetime.now().astimezone(ZoneInfo('Asia/Bangkok'))
        overtimes_start_at = overtimes.start_at.astimezone(ZoneInfo('Asia/Bangkok'))
        overtimes_end_at = overtimes.end_at.astimezone(ZoneInfo('Asia/Bangkok'))
        
        failed_response = {
            'success': False, 
            'errors': [], 
            'modal_messages':[],
            'is_close_modal':False,
        }

        if overtimes_end_at < now:
            failed_response['toast_message'] = 'Overtime Already Ended'
            return JsonResponse(failed_response)
        
        if overtimes_start_at < now:
            failed_response['toast_message'] = 'Overtime Already Started'
            return JsonResponse(failed_response)

        if overtimes.deleted_at:
            failed_response['toast_message'] = 'Overtime Already Deleted'
            return JsonResponse(failed_response)
        
        # Check if overtime users is valid uuid
        added_overtime_users, removed_overtime_users, reactivated_overtime_users = [], [], []
        for ovt_user in request.POST['overtime_users[]'].split(','):
            try:
                if uuid.UUID(ovt_user, version=4):
                    employee = get_object_or_404(Employees, hash_uuid=ovt_user)
                    added_overtime_users.append(employee.id)
            except ValueError as ve:
                failed_response['toast_message'] = 'Invalid Employee UUID'
                return JsonResponse(failed_response)


        # Check Is There Any Inactive Overtime Users in user Input
        # If There is, then it's reactivated
        inactive_overtime_users = OvertimeUsers.objects.filter(overtime_id = overtimes, status = 0).values_list('employee_id', flat=True)
        for ovt_user in inactive_overtime_users:
            try: 
                added_overtime_users.remove(ovt_user)
                reactivated_overtime_users.append(ovt_user)
            except: pass
        
        # Check Is There Any Active Overtime Users in user Input
        # If There isn't , then it's removed
        active_overtime_users = OvertimeUsers.objects.filter(overtime_id = overtimes, status = 1).values_list('employee_id', flat=True)
        for ovt_user in active_overtime_users:
            try: added_overtime_users.remove(ovt_user) 
            except: removed_overtime_users.append(ovt_user)


        if overtimes_form.is_valid():
            
            # Check if start_at is greater than end_at 
            if overtimes_form.cleaned_data['start_at'] >= overtimes_form.cleaned_data['end_at']:
                failed_response['toast_message'] = 'End At Must Greater Than Start At'
                return JsonResponse(failed_response)
            
            # Check if start_at or end_at is less than current time
            if overtimes_form.cleaned_data['start_at'] < now:
                failed_response['toast_message'] = 'Start At Must Greater Than Current Time'
                return JsonResponse(failed_response)
            
            if overtimes_form.cleaned_data['end_at'] < now:
                failed_response['toast_message'] = 'End At Must Greater Than Current Time'
                return JsonResponse(failed_response)

            try:
                # Add Additional Field to Database
                overtimes_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                overtimes_form.cleaned_data['updated_by'] = request.user

                # Saving Data to Database
                overtimes_form.save()

                if added_overtime_users:
                    overtime_users_data = {
                        'overtime_id': overtimes,
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                        'updated_at': None,
                        'updated_by': None,
                        'deleted_at': None,
                        'deleted_by': None,
                    }
                    
                    for ovt_user in added_overtime_users:
                        overtime_users_data['employee_id'] = get_object_or_404(Employees, id=ovt_user)
                        OvertimeUsers(**overtime_users_data).save()


                if removed_overtime_users:
                    for ovt_user in removed_overtime_users:
                        employee = get_object_or_404(Employees, id=ovt_user)
                        overtime_user = get_object_or_404(OvertimeUsers, overtime_id=overtimes, employee_id= employee)
                        overtime_user.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        overtime_user.deleted_by = request.user
                        overtime_user.status = 0
                        overtime_user.save()


                if reactivated_overtime_users:
                    for ovt_user in reactivated_overtime_users:
                        employee = get_object_or_404(Employees, id=ovt_user)
                        overtime_user = get_object_or_404(OvertimeUsers, overtime_id=overtimes, employee_id= employee)
                        overtime_user.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        overtime_user.updated_by = request.user
                        overtime_user.status = 1
                        overtime_user.save()

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
                'toast_message':'Overtime Updated Successfuly',
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
            for field, error_list in overtimes_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailOvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes']

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
    
    def get(self, request, overtime_uuid):
        overtimes_object = get_object_or_404(Overtimes, hash_uuid=overtime_uuid)
        overtimes_form = OvertimesForm(instance=overtimes_object)

        for key in overtimes_form.fields:
            overtimes_form.fields[key].widget.attrs['disabled'] = True
            overtimes_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'overtimes_form':overtimes_form,
            'modal_title':'view overtimes',
        }
        
        form = render_to_string('overtimes/includes/overtimes_form.html', context, request=request)

        overtime_users_data = []
        overtime_users_object = OvertimeUsers.objects.filter(overtime_id = overtimes_object)
        for ou in overtime_users_object:
            nik = ou.employee_id.nik if ou.employee_id.nik else '-'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            nik_name = nik + '<br>' + ou.employee_id.name
            department_members_object = DepartmentMembers.objects.filter(employee_id=ou.employee_id.id, status=1)
            departments = [ x.department_id.name for x in department_members_object ]
            overtime_users_data.append({
                'uq_employee': ou.employee_id.hash_uuid,
                'nik_name': nik_name,
                'departments': departments,
                'status' : ou.status,
                'action': '',
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
            'overtime_users_data': overtime_users_data,
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class DeleteOvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes', 'overtimes.delete_overtimes']

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

    def post(self, request, overtime_uuid):
        overtime = get_object_or_404(Overtimes, hash_uuid=overtime_uuid)
        overtime.status = 0
        overtime.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        overtime.deleted_by = request.user
        overtime.save()

        response = {
            'success': True, 
            'toast_message':'Overtime Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class OvertimesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes']

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
            'title':'Overtimes',
        }

        return render(request, 'overtimes/overtimes.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class AddOvertimesUsersView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['overtimes.read_overtimes', 'overtimes.create_overtime_users']

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
        try:
            if uuid.UUID(request.POST['employee'], version=4):
                employee_object = get_object_or_404(Employees, hash_uuid=request.POST['employee'])
                
                department_members_object = DepartmentMembers.objects.filter(employee_id=employee_object.id, status=1)
                departments_name = [ x.department_id.name for x in department_members_object ]
                departments_name = ', '.join(departments_name)

                icons = '''
                    <div class="d-flex justify-content-center">
                        <span class="delete-overtimes-users btn text-danger w-100">
                            <i class="bi bi-trash"></i>
                        </span>
                    </div>
                '''

                nik = employee_object.nik if employee_object.nik else '-'
                nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
                nik_name = nik + '<br>' + employee_object.name
                employee_data = {
                    'uq_employee':  employee_object.hash_uuid,
                    'nik_name': nik_name,
                    'status': employee_object.status,
                    'departments': departments_name,
                    'action':icons,
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
        
        except ValueError as ve:
            response = {
                'success':False,
                'toast_message':'Invalid Choices',
            }
                
            return JsonResponse(response)
