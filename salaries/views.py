from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User, Permission
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from salaries.forms import PayrollPeriodsForm

from .models import PayrollPeriods

from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
# Create your views here.
 
class ListSalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'view_link':str(reverse_lazy('salaries:detail-salaries', args=["@@"])),
            'update_link': str(reverse_lazy('salaries:update-salaries', args=["@@"])),
            'delete_link':str(reverse_lazy('salaries:delete-salaries', args=["@@"])),
        }

        payroll_period_object = PayrollPeriods.objects.all()
        payroll_periods_data = []

        for pp in payroll_period_object:
            context['hash'] = pp.hash_uuid
            form_action = render_to_string('salaries/includes/payroll_periods_form_action_button.html', context, request=request)
            
            payroll_periods_data.append({
                'name':pp.name,
                'description':pp.description,
                'start_at': pp.start_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'end_at': pp.end_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'status': pp.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'payroll_periods_data': payroll_periods_data
        }

        return JsonResponse(response)

    def post(self, request):
        pass
    
class CreateSalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request):
        pass
    
class UpdateSalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request):
        pass
  
class DetailSalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request):
        pass
    
class DeleteSalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request):
        pass

class SalariesView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        context = {
            'title':'Salaries',
        }

        return render(request, 'salaries/salaries.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class ListPayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
            'view_link':str(reverse_lazy('salaries:detail-payroll-periods', args=["@@"])),
            'update_link': str(reverse_lazy('salaries:update-payroll-periods', args=["@@"])),
            'delete_link':str(reverse_lazy('salaries:delete-payroll-periods', args=["@@"])),
        }

        payroll_period_object = PayrollPeriods.objects.all()
        payroll_periods_data = []

        for pp in payroll_period_object:
            context['hash'] = pp.hash_uuid
            form_action = render_to_string('salaries/includes/payroll_periods_form_action_button.html', context, request=request)
            
            payroll_periods_data.append({
                'name':pp.name,
                'description':pp.description,
                'start_at': pp.start_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'end_at': pp.end_at.astimezone(ZoneInfo('Asia/Bangkok')).date().strftime("%d %B %Y"),
                'status': pp.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'payroll_periods_data': payroll_periods_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class CreatePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.create_payroll_period']

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
        payroll_periods_form = PayrollPeriodsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create payroll period',
            'payroll_periods_form':payroll_periods_form,
            'uq':{
                'create_link':str(reverse_lazy('salaries:create-payroll-periods')),
            }
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        print(request.POST)

        payroll_periods_form = PayrollPeriodsForm(request.POST or None)

        if payroll_periods_form.is_valid():
            print('Payroll Periods Form is Valid')
            
            try:
                print('SAVING TO DB')
                payroll_period_data = payroll_periods_form.cleaned_data

                # Add Additional Benefits Field to Database
                payroll_period_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                payroll_period_data['created_by'] = request.user
                payroll_period_data['updated_at'] = None
                payroll_period_data['updated_by'] = None
                payroll_period_data['deleted_at'] = None
                payroll_period_data['deleted_by'] = None

                print(payroll_period_data)

                PayrollPeriods(**payroll_period_data).save()

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
                'toast_message':'Payroll Period Added Successfuly',
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

            for field, error_list in payroll_periods_form.errors.items():
                errors[field] = error_list

            print('ERRORS')
            print(errors)

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class UpdatePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.update_payroll_period']

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
    
    def get(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)

        payroll_periods_form = PayrollPeriodsForm(instance=payroll_period)

        context = {
            'mode':'update',
            'payroll_periods_form':payroll_periods_form,
            'modal_title':'update payroll period',
            'uq':{
                'hash': period_uuid,
                'update_link':str(reverse_lazy('salaries:update-payroll-periods', args=["@@"])),
            }
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
        }

        return JsonResponse(response)

    def post(self, request, period_uuid):
        print(request.POST)
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)

        payroll_period_form = PayrollPeriodsForm(request.POST or None, instance=payroll_period)

        if payroll_period_form.is_valid():
            print('Form is Valid')
            
            try:
                print('SAVING TO DB')

                # Add Additional Field to Database
                payroll_period_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                payroll_period_form.cleaned_data['updated_by'] = request.user
                
                # Saving Payroll Period to Database
                payroll_period_form.save()

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
                'toast_message':'Payroll Period Updated Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            print('ERRORS')
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}
            for field, error_list in payroll_period_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class DetailPayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
    
    def get(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)

        payroll_periods_form = PayrollPeriodsForm(instance=payroll_period)

        for key in payroll_periods_form.fields:
            payroll_periods_form.fields[key].widget.attrs['disabled'] = True
            payroll_periods_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'payroll_periods_form':payroll_periods_form,
            'modal_title':'view payroll period',
        }
        
        form = render_to_string('salaries/includes/payroll_periods_form.html', context, request=request)

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

class DeletePayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period', 'salaries.delete_payroll_period']

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

    def post(self, request, period_uuid):
        payroll_period = get_object_or_404(PayrollPeriods, hash_uuid=period_uuid)
        payroll_period.status = 0
        payroll_period.save()

        response = {
            'success': True, 
            'toast_message':'Payroll Period Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class PayrollPeriodView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['salaries.read_payroll_period']

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
            'title':'Payroll Period',
        }

        return render(request, 'salaries/payroll_periods.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))