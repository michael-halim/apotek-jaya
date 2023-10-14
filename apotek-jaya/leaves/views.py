from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .models import Leaves, LeaveBalances
from .forms import LeavesForm, LeaveBalancesForm
from departments.models import DepartmentMembers
from employees.models import Employees

from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

class ListLeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves']

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
            'view_link':str(reverse_lazy('leaves:detail-leaves', args=["@@"])),
            'update_link': str(reverse_lazy('leaves:update-leaves', args=["@@"])),
            'delete_link':str(reverse_lazy('leaves:delete-leaves', args=["@@"])),
        }

        leaves_object = Leaves.objects.all()
        leaves_data = []

        for leave in leaves_object:
            context['hash'] = leave.hash_uuid
            form_action = render_to_string('leaves/includes/leaves_form_action_button.html', context, request=request)
            
            leaves_data.append({
                'name':leave.name,
                'description':leave.description,
                'max_duration':leave.max_duration,
                'created_at': leave.created_at.date().strftime("%d %B %Y"),
                'status':leave.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'leaves_data': leaves_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class CreateLeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves', 'leaves.create_leaves']

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
        leaves_form = LeavesForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create leaves',
            'leaves_form':leaves_form,
            'uq':{
                'create_link':str(reverse_lazy('leaves:create-leaves')),
            }
        }
        
        form = render_to_string('leaves/includes/leaves_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }
        
        return JsonResponse(response)

    def post(self, request):
        leaves_form = LeavesForm(request.POST or None)

        if leaves_form.is_valid():
            try:
                leaves_data = leaves_form.cleaned_data

                # Add Additional Field to Database
                leaves_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                leaves_data['created_by'] = request.user
                leaves_data['updated_at'] = None
                leaves_data['updated_by'] = None
                leaves_data['deleted_at'] = None
                leaves_data['deleted_by'] = None

                Leaves(**leaves_data).save()

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
                'toast_message':'Leave Added Successfuly',
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

            for field, error_list in leaves_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)
    
class UpdateLeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves', 'leaves.update_leaves']

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
    
    def get(self, request, leave_uuid):
        leaves_object = get_object_or_404(Leaves, hash_uuid=leave_uuid)
        leaves_form = LeavesForm(instance=leaves_object)

        context = {
            'mode':'update',
            'leaves_form':leaves_form,
            'modal_title':'update leaves',
            'uq':{
                'hash': leave_uuid,
                'update_link':str(reverse_lazy('leaves:update-leaves', args=["@@"])),
            }
        }
        
        form = render_to_string('leaves/includes/leaves_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }

        return JsonResponse(response)

    def post(self, request, leave_uuid):
        leave_object = get_object_or_404(Leaves, hash_uuid=leave_uuid)
        leaves_form = LeavesForm(request.POST or None, instance=leave_object)

        if leaves_form.is_valid():
            try:
                # Add Additional Field to Database
                leaves_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                leaves_form.cleaned_data['updated_by'] = request.user

                # Saving Data to Database
                leaves_form.save()

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
                'toast_message':'Leave Updated Successfuly',
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
            for field, error_list in leaves_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)
    
class DetailLeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves']

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
    
    def get(self, request, leave_uuid):
        leaves_object = get_object_or_404(Leaves, hash_uuid=leave_uuid)
        leaves_form = LeavesForm(instance=leaves_object)

        for key in leaves_form.fields:
            leaves_form.fields[key].widget.attrs['disabled'] = True
            leaves_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'leaves_form':leaves_form,
            'modal_title':'view leaves',
        }
        
        form = render_to_string('leaves/includes/leaves_form.html', context, request=request)

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
    
class DeleteLeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves', 'leaves.delete_leaves']

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

    def post(self, request, leave_uuid):
        leave = get_object_or_404(Leaves, hash_uuid=leave_uuid)
        leave.status = 0
        leave.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        leave.deleted_by = request.user
        leave.save()

        response = {
            'success': True, 
            'toast_message':'Leave Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)
    
class LeavesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leaves']

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
            'title':'Leaves',
        }

        return render(request, 'leaves/leaves.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class ListLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances']

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
            'view_link':str(reverse_lazy('leaves:detail-leaves-balances', args=["@@"])),
            'update_link': str(reverse_lazy('leaves:update-leaves-balances', args=["@@"])),
            'delete_link':str(reverse_lazy('leaves:delete-leaves-balances', args=["@@"])),
        }

        leaves_balances_object = LeaveBalances.objects.filter(status=1).distinct('employee_id')
        leaves_balances_data = []

        for lb in leaves_balances_object:
            context['hash'] = lb.hash_uuid
            form_action = render_to_string('leaves/includes/leaves_balances_form_action_button.html', context, request=request)
            department_object = DepartmentMembers.objects.filter(employee_id=lb.employee_id)
            departments_name = [ x.department_id.name for x in department_object ]
            departments_name = ', '.join(departments_name)
            nik = lb.employee_id.nik if lb.employee_id.nik else '-'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            nik_name = nik + '<br>' + lb.employee_id.name

            leaves_balances_data.append({
                'nik_name':nik_name,
                'departments': departments_name,
                'expired_at': lb.expired_at.strftime("%d %B %Y"),
                'uq': form_action, 
            })

        response = {
            'success':True,
            'leaves_balances_data': leaves_balances_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreateLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances', 'leaves.create_leave_balances']

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
        leaves_balances_form = LeaveBalancesForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create leaves balances',
            'leaves_balances_form':leaves_balances_form,
            'uq':{
                'create_link':str(reverse_lazy('leaves:create-leaves-balances')),
            }
        }
        
        form = render_to_string('leaves/includes/leaves_balances_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'mode': 'create',
            'is_view_only': False,
        }
        
        return JsonResponse(response)

    def post(self, request):
        failed_response = {
            'success': False, 
            'errors': [], 
            'modal_messages':[],
            'is_close_modal':False,
        }

        # Check Leave UUID
        leaves_balances_employee = []
        for lb in request.POST['leaves_balances_employee[]'].split(','):
            try:
                if uuid.UUID(lb, version=4):
                    leaves_balances_employee.append(get_object_or_404(Leaves, hash_uuid=lb))

            except ValueError as ve:
                failed_response['toast_message'] = 'Invalid Leave UUID'
                return JsonResponse(failed_response)
        
        # Check Balance
        leaves_balances_count = []
        for blc in request.POST['leaves_balances_count[]'].split(','):
            if blc.isnumeric():
                leaves_balances_count.append(blc)
            else:
                failed_response['toast_message'] = 'Balance Must Be Numeric'
                return JsonResponse(failed_response)
        
        # Check Employee UUID
        employee_uuid = request.POST['employee_id']
        employee_object = None
        try:
            if uuid.UUID(employee_uuid, version=4):
                employee_object = get_object_or_404(Employees, hash_uuid=employee_uuid)
        
        except ValueError as ve:
            failed_response['toast_message'] = 'Invalid Employee UUID'
            return JsonResponse(failed_response)
        

        if len(leaves_balances_count) != len(leaves_balances_employee):
            failed_response['toast_message'] = 'Invalid Balance or Leave'
            return JsonResponse(failed_response)

        if employee_object is None:
            failed_response['toast_message'] = 'Invalid Employee'
            return JsonResponse(failed_response)
        
        leaves_balances_form = LeaveBalancesForm(request.POST or None)

        if leaves_balances_form.is_valid():
            try:
                leaves_balances_data = leaves_balances_form.cleaned_data

                # Add Additional Field to Database
                leaves_balances_data['employee_id'] = employee_object
                leaves_balances_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                leaves_balances_data['created_by'] = request.user
                leaves_balances_data['updated_at'] = None
                leaves_balances_data['updated_by'] = None
                leaves_balances_data['deleted_at'] = None
                leaves_balances_data['deleted_by'] = None

                for leave, balance in zip(leaves_balances_employee, leaves_balances_count):
                    leaves_balances_data['leave_id'] = leave
                    leaves_balances_data['balance'] = balance
                    LeaveBalances(**leaves_balances_data).save()

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
                'toast_message':'Leave Balances Added Successfuly',
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

            for field, error_list in leaves_balances_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdateLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances', 'leaves.update_leave_balances']

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
    
    def get(self, request, leave_balance_uuid):
        leaves_balance_object = get_object_or_404(LeaveBalances, hash_uuid=leave_balance_uuid)

        initial_data = {
            'employee_id':leaves_balance_object.employee_id,
        }

        leaves_balances_form = LeaveBalancesForm(instance=leaves_balance_object, initial=initial_data)
        
        leaves_balances_form.fields['employee_id'].widget.attrs['disabled'] = True
        leaves_balances_form.fields['employee_id'].widget.attrs['placeholder'] = ''

        context = {
            'mode':'update',
            'leaves_balances_form':leaves_balances_form,
            'modal_title':'update leave balances',
            'uq':{
                'hash': leave_balance_uuid,
                'update_link':str(reverse_lazy('leaves:update-leaves-balances', args=["@@"])),
            }
        }
        
        form = render_to_string('leaves/includes/leaves_balances_form.html', context, request=request)

        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-leaves-balances-employee btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        leaves_balances_data = []
        leaves_balances_employee = LeaveBalances.objects.filter(employee_id = leaves_balance_object.employee_id, status=1)
        for lb in leaves_balances_employee:
            leaves_balances_data.append({
                'uq_leave': lb.leave_id.hash_uuid,
                'name': lb.leave_id.name,
                'description': lb.leave_id.description,
                'balance' : lb.balance,
                'action': trash_icon,
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            'mode': 'update',
            'leaves_balances_data': leaves_balances_data,
        }

        return JsonResponse(response)

    def post(self, request, leave_balance_uuid):
        employee = get_object_or_404(Employees, hash_uuid=request.POST['employee_id'])
        leave_balance_object = get_object_or_404(LeaveBalances, hash_uuid=leave_balance_uuid)
        leave_balances_form = LeaveBalancesForm(request.POST or None)
        
        failed_response = {
            'success': False, 
            'errors': [], 
            'modal_messages':[],
            'is_close_modal':False,
        }

        if leave_balance_object.employee_id != employee:
            failed_response['toast_message'] = 'You\'re not allowed to change employee'
            return JsonResponse(response)
        
        # Check Leave UUID
        added_leaves_balances, removed_leaves_balances = {}, {}
        leaves_balances_employee = request.POST['leaves_balances_employee[]'].split(',')
        leaves_balances_count = request.POST['leaves_balances_count[]'].split(',')
        
        if len(leaves_balances_count) != len(leaves_balances_employee):
            failed_response['toast_message'] = 'Invalid Balance or Leave'
            return JsonResponse(failed_response)
        
        if len(leaves_balances_count) > 0 and len(leaves_balances_employee) > 0:
            for leave, count in zip(leaves_balances_employee, leaves_balances_count):
                try:
                    if uuid.UUID(leave, version=4):
                        if count.isnumeric():
                            added_leaves_balances[leave] = count

                except ValueError as ve:
                    failed_response['toast_message'] = 'Invalid Leave UUID'
                    return JsonResponse(failed_response)
            
        active_leaves_balance = LeaveBalances.objects.filter(employee_id=leave_balance_object.employee_id, status=1)
        for lb in active_leaves_balance:
            if str(lb.leave_id.hash_uuid) in added_leaves_balances:
                del added_leaves_balances[str(lb.leave_id.hash_uuid)]
            else:
                removed_leaves_balances[str(lb.leave_id.hash_uuid)] = lb.balance

        if leave_balances_form.is_valid():
            try:
                if added_leaves_balances:
                    leaves_balances_data = {
                        'employee_id': leave_balance_object.employee_id,
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                        'updated_at': None,
                        'updated_by': None,
                        'deleted_at': None,
                        'deleted_by': None,
                        'expired_at': leave_balances_form.cleaned_data['expired_at'],
                    }
                    
                    for lb in added_leaves_balances:
                        leaves_balances_data['leave_id'] = get_object_or_404(Leaves, hash_uuid=lb)
                        leaves_balances_data['balance'] = added_leaves_balances[lb]

                        LeaveBalances(**leaves_balances_data).save()

                if removed_leaves_balances:
                    for lb in removed_leaves_balances:
                        leave = get_object_or_404(Leaves, hash_uuid=lb)
                        leaves_balances = get_object_or_404(LeaveBalances, leave_id=leave)
                        leaves_balances.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        leaves_balances.deleted_by = request.user
                        leaves_balances.status = 0
                        leaves_balances.save()

                if len(removed_leaves_balances) == 0 and len(added_leaves_balances) == 0:
                    updated_leaves_balances = LeaveBalances.objects.filter(employee_id=leave_balance_object.employee_id, status=1)
                    for lb in updated_leaves_balances:
                        lb.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        lb.updated_by = request.user
                        lb.expired_at = leave_balances_form.cleaned_data['expired_at']
                        lb.save()

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
                'toast_message':'Leave Balances Updated Successfuly',
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
            for field, error_list in leave_balances_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances']

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
    
    def get(self, request, leave_balance_uuid):
        leaves_balance_object = get_object_or_404(LeaveBalances, hash_uuid=leave_balance_uuid)

        initial_data = {
            'employee_id':leaves_balance_object.employee_id,
        }

        leaves_balances_form = LeaveBalancesForm(instance=leaves_balance_object, initial=initial_data)

        for key in leaves_balances_form.fields:
            leaves_balances_form.fields[key].widget.attrs['disabled'] = True
            leaves_balances_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'leaves_balances_form':leaves_balances_form,
            'modal_title':'view leave balances',
        }
        
        form = render_to_string('leaves/includes/leaves_balances_form.html', context, request=request)

        leaves_balances_data = []
        leaves_balances_employee = LeaveBalances.objects.filter(employee_id = leaves_balance_object.employee_id, status=1)
        for lb in leaves_balances_employee:
            leaves_balances_data.append({
                'uq_leave': lb.hash_uuid,
                'name': lb.leave_id.name,
                'description': lb.leave_id.description,
                'balance' : lb.balance,
                'action': '',
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
            'leaves_balances_data': leaves_balances_data,
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class DeleteLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances', 'leaves.delete_leave_balances']

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

    def post(self, request, leave_balance_uuid):
        leave_balance = get_object_or_404(LeaveBalances, hash_uuid=leave_balance_uuid)
        leave_balance.status = 0
        leave_balance.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        leave_balance.deleted_by = request.user
        leave_balance.save()

        response = {
            'success': True, 
            'toast_message':'Leave Balance Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class LeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances']

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
            'title':'Leaves Balances',
        }

        return render(request, 'leaves/leaves_balances.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class AddLeavesBalancesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['leaves.read_leave_balances', 'leaves.create_leave_balances']

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
        failed_response = {
            'success': False, 
            'errors': [], 
            'modal_messages':[],
            'is_close_modal':False,
        }

        leave = None
            
        if request.POST['leave_id'] == '':
            failed_response['toast_message'] = 'Please Select Leave'
            return JsonResponse(failed_response)
        
        else:
            try:
                if uuid.UUID(request.POST['leave_id']):
                    leave = get_object_or_404(Leaves, hash_uuid=request.POST['leave_id'])
            except ValueError as ve:
                failed_response['toast_message'] = 'Invalid Leave'
                return JsonResponse(failed_response)
        
        if request.POST['balance'] == '' or request.POST['balance'] == '0':
            failed_response['toast_message'] = 'Please Fill Balance'
            return JsonResponse(failed_response)
        
        if not request.POST['balance'].isnumeric():
            failed_response['toast_message'] = 'Balance Must Be Numeric'
            return JsonResponse(failed_response)
        
        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-leaves-balances-employee btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        leaves_data = {
            'uq_leave': leave.hash_uuid,
            'name': leave.name,
            'description': leave.description,
            'balance': request.POST['balance'],
            'action': trash_icon,
        }

        response = {
            'success': True,
            'toast_message':'Leave Balance Added Successfuly',
            'is_close_modal':False,
            'leaves_data': leaves_data,
        }

        return JsonResponse(response)