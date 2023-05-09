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

from .forms import BenefitsForm
from .models import Benefits

from employees.models import Employees

from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

class ListBenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits']

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
            'view_link':str(reverse_lazy('benefits:detail-benefits', args=["@@"])),
            'update_link': str(reverse_lazy('benefits:update-benefits', args=["@@"])),
            'delete_link':str(reverse_lazy('benefits:delete-benefits', args=["@@"])),
        }

        benefits_object = Benefits.objects.all()
        benefits_data = []

        for benefit in benefits_object:
            context['hash'] = benefit.hash_uuid
            form_action = render_to_string('benefits/includes/form_action_button.html', context, request=request)
            
            benefits_data.append({
                'name':benefit.name,
                'description':benefit.description,
                'value':benefit.value,
                'created_at': benefit.created_at.date().strftime("%d %B %Y"),
                'status':benefit.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'benefits_data': benefits_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreateBenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits', 'benefits.create_benefits']

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
        print('benefit get create')
        benefits_form = BenefitsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create benefits',
            'benefits_form':benefits_form,
            'uq':{
                'create_link':str(reverse_lazy('benefits:create-benefits')),
            }
        }
        
        form = render_to_string('benefits/includes/form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        print(request.POST)

        benefits_form = BenefitsForm(request.POST or None)

        if benefits_form.is_valid():
            print('Benefits Form is Valid')
            
            try:
                print('SAVING TO DB')
                benefits_data = benefits_form.cleaned_data

                # Add Additional Benefits Field to Database
                benefits_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefits_data['created_by'] = request.user
                benefits_data['updated_at'] = None
                benefits_data['updated_by'] = None
                benefits_data['deleted_at'] = None
                benefits_data['deleted_by'] = None

                print(benefits_data)

                Benefits(**benefits_data).save()

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
                'toast_message':'Benefits Added Successfuly',
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

            for field, error_list in benefits_form.errors.items():
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

class UpdateBenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits', 'benefits.update_benefits']

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
    
    def get(self, request, benefit_uuid):
        benefit = get_object_or_404(Benefits, hash_uuid=benefit_uuid)

        benefits_form = BenefitsForm(instance=benefit)

        context = {
            'mode':'update',
            'benefits_form':benefits_form,
            'modal_title':'update benefits',
            'uq':{
                'hash': benefit_uuid,
                'update_link':str(reverse_lazy('benefits:update-benefits', args=["@@"])),
            }
        }
        
        form = render_to_string('benefits/includes/form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request, benefit_uuid):
        print(request.POST)
        benefit = get_object_or_404(Benefits, hash_uuid=benefit_uuid)
        benefit_form = BenefitsForm(request.POST or None, instance=benefit)

        if benefit_form.is_valid():
            print('Form is Valid')
            
            try:
                print('SAVING TO DB')

                # Add Additional Field to Database
                benefit_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_form.cleaned_data['updated_by'] = request.user

                # Saving Benefits to Database
                benefit_form.save()

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
                'toast_message':'Benefit Updated Successfuly',
                'is_close_modal':True
            }

            return JsonResponse(response)

        else:
            print('ERRORS')
            print(benefit_form.errors)
            messages.error(request,'Please Correct The Errors Below')
            
            modal_messages = []
            for message in messages.get_messages(request):
                modal_messages.append({
                    'message':str(message),
                    'tags': message.tags
                })

            errors = {}
            for field, error_list in benefit_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailBenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits']

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
    
    def get(self, request, benefit_uuid):
        benefit = get_object_or_404(Benefits, hash_uuid=benefit_uuid)

        benefits_form = BenefitsForm(instance=benefit)

        for key in benefits_form.fields:
            benefits_form.fields[key].widget.attrs['disabled'] = True
            benefits_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'benefits_form':benefits_form,
            'modal_title':'view benefits',
        }
        
        form = render_to_string('benefits/includes/form.html', context, request=request)

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
    
class DeleteBenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits', 'benefits.delete_benefits']

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

    def post(self, request, benefit_uuid):
        benefit = get_object_or_404(Benefits, hash_uuid=benefit_uuid)
        benefit.status = 0
        benefit.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        benefit.deleted_by = request.user
        benefit.save()

        response = {
            'success': True, 
            'toast_message':'Benefit Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)
    
class BenefitsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefits']

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
            'title':'Benefits',
        }

        return render(request, 'benefits/benefits.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))