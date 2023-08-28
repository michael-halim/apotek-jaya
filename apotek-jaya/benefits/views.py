from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .forms import BenefitCategoriesForm, BenefitSchemeForm, BenefitsForm, DetailEmployeeBenefitsForm, PTKPTypeForm
from .models import BenefitAdjustments, BenefitCategories, BenefitScheme, Benefits, DetailEmployeeBenefits, PTKPType
from employees.models import Employees
from departments.models import DepartmentMembers, Departments

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
            form_action = render_to_string('benefits/includes/benefits_form_action_button.html', context, request=request)
            
            benefits_data.append({
                'name':benefit.name,
                'description':benefit.description,
                'category':benefit.benefit_category_id.name,
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
        
        form = render_to_string('benefits/includes/benefits_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        benefits_form = BenefitsForm(request.POST or None)

        if benefits_form.is_valid():
            try:
                benefits_data = benefits_form.cleaned_data

                # Add Additional Field to Database
                benefits_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefits_data['created_by'] = request.user
                benefits_data['updated_at'] = None
                benefits_data['updated_by'] = None
                benefits_data['deleted_at'] = None
                benefits_data['deleted_by'] = None

                Benefits(**benefits_data).save()

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
        
        initial_data = {
            'benefit_category_id':benefit.benefit_category_id
        }
        benefits_form = BenefitsForm(instance=benefit, initial=initial_data)

        context = {
            'mode':'update',
            'benefits_form':benefits_form,
            'modal_title':'update benefits',
            'uq':{
                'hash': benefit_uuid,
                'update_link':str(reverse_lazy('benefits:update-benefits', args=["@@"])),
            }
        }
        
        form = render_to_string('benefits/includes/benefits_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request, benefit_uuid):
        benefit = get_object_or_404(Benefits, hash_uuid=benefit_uuid)
        benefit_form = BenefitsForm(request.POST or None, instance=benefit)

        if benefit_form.is_valid():
            try:

                # Add Additional Field to Database
                benefit_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_form.cleaned_data['updated_by'] = request.user

                # Saving Benefits to Database
                benefit_form.save()

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
                'toast_message':'Benefit Updated Successfuly',
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

        initial_data = {
            'benefit_category_id':benefit.benefit_category_id
        }
        benefits_form = BenefitsForm(instance=benefit, initial=initial_data)

        for key in benefits_form.fields:
            benefits_form.fields[key].widget.attrs['disabled'] = True
            benefits_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'benefits_form':benefits_form,
            'modal_title':'view benefits',
        }
        
        form = render_to_string('benefits/includes/benefits_form.html', context, request=request)

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
    
class ListBenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories']

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
            'view_link':str(reverse_lazy('benefits:detail-benefit-categories', args=["@@"])),
            'update_link': str(reverse_lazy('benefits:update-benefit-categories', args=["@@"])),
            'delete_link':str(reverse_lazy('benefits:delete-benefit-categories', args=["@@"])),
        }

        benefit_categories_object = BenefitCategories.objects.all()
        benefit_categories_data = []

        for benefit_category in benefit_categories_object:
            context['hash'] = benefit_category.hash_uuid
            form_action = render_to_string('benefits/includes/benefit_categories_form_action_button.html', context, request=request)
            
            benefit_categories_data.append({
                'name':benefit_category.name,
                'created_at': benefit_category.created_at.date().strftime("%d %B %Y"),
                'status': benefit_category.status,
                'uq': form_action,
            })

        response = {
            'success':True,
            'benefit_categories_data': benefit_categories_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class CreateBenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories', 'benefits.create_benefit_categories']

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
        benefit_categories_form = BenefitCategoriesForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create benefit categories',
            'benefit_categories_form':benefit_categories_form,
            'uq':{
                'create_link':str(reverse_lazy('benefits:create-benefit-categories')),
            }
        }
        
        form = render_to_string('benefits/includes/benefit_categories_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }

        return JsonResponse(response)

    def post(self, request):
        benefit_categories_form = BenefitCategoriesForm(request.POST or None)

        if benefit_categories_form.is_valid():
            try:
                benefit_categories_data = benefit_categories_form.cleaned_data

                # Add Additional Field to Database
                benefit_categories_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_categories_data['created_by'] = request.user
                benefit_categories_data['updated_at'] = None
                benefit_categories_data['updated_by'] = None
                benefit_categories_data['deleted_at'] = None
                benefit_categories_data['deleted_by'] = None

                BenefitCategories(**benefit_categories_data).save()

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
                'toast_message':'Benefit Categories Added Successfuly',
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

            for field, error_list in benefit_categories_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdateBenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories', 'benefits.update_benefit_categories']

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
    
    def get(self, request, benefit_category_uuid):
        benefit_category = get_object_or_404(BenefitCategories, hash_uuid=benefit_category_uuid)
        benefit_categories_form = BenefitsForm(instance=benefit_category)

        context = {
            'mode':'update',
            'benefit_categories_form':benefit_categories_form,
            'modal_title':'update benefit categories',
            'uq':{
                'hash': benefit_category_uuid,
                'update_link':str(reverse_lazy('benefits:update-benefit-categories', args=["@@"])),
            }
        }
        
        form = render_to_string('benefits/includes/benefit_categories_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request, benefit_category_uuid):
        benefit_category = get_object_or_404(BenefitCategories, hash_uuid=benefit_category_uuid)
        benefit_categories_form = BenefitCategoriesForm(request.POST or None, instance=benefit_category)

        if benefit_categories_form.is_valid():
            try:

                # Add Additional Field to Database
                benefit_categories_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_categories_form.cleaned_data['updated_by'] = request.user

                # Saving Data to Database
                benefit_categories_form.save()

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
                'toast_message':'Benefit Categories Updated Successfuly',
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
            for field, error_list in benefit_categories_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class DetailBenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories']

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

    def get(self, request, benefit_category_uuid):
        benefit_category = get_object_or_404(BenefitCategories, hash_uuid=benefit_category_uuid)
        benefit_categories_form = BenefitCategoriesForm(instance=benefit_category)

        for key in benefit_categories_form.fields:
            benefit_categories_form.fields[key].widget.attrs['disabled'] = True
            benefit_categories_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'benefit_categories_form':benefit_categories_form,
            'modal_title':'view benefit categories',
        }
        
        form = render_to_string('benefits/includes/benefit_categories_form.html', context, request=request)

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

    
class DeleteBenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories', 'benefits.delete_benefit_categories']

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

    def post(self, request, benefit_category_uuid):
        benefit_category = get_object_or_404(BenefitCategories, hash_uuid=benefit_category_uuid)
        benefit_category.status = 0
        benefit_category.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        benefit_category.deleted_by = request.user
        benefit_category.save()

        response = {
            'success': True, 
            'toast_message':'Benefit Category Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class BenefitCategoriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_categories']

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
            'title':'Benefit Categories',
        }

        return render(request, 'benefits/benefit_categories.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class ListBenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme']

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
            'view_link':str(reverse_lazy('benefits:detail-benefit-scheme', args=["@@"])),
            'update_link': str(reverse_lazy('benefits:update-benefit-scheme', args=["@@"])),
            'delete_link':str(reverse_lazy('benefits:delete-benefit-scheme', args=["@@"])),
        }

        benefit_scheme_object = BenefitScheme.objects.all()
        benefit_scheme_data = []

        for benefit_scheme in benefit_scheme_object:
            context['hash'] = benefit_scheme.hash_uuid
            form_action = render_to_string('benefits/includes/benefit_scheme_form_action_button.html', context, request=request)
            
            benefit_scheme_data.append({
                'name':benefit_scheme.name,
                'description':benefit_scheme.description,
                'created_at': benefit_scheme.created_at.date().strftime("%d %B %Y"),
                'status': benefit_scheme.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'benefit_scheme_data': benefit_scheme_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))


class CreateBenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme', 'benefits.create_benefit_scheme']

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
        benefit_scheme_form = BenefitSchemeForm()
        detail_employee_benefits_form = DetailEmployeeBenefitsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create benefit scheme',
            'benefit_scheme_form':benefit_scheme_form,
            'detail_employee_benefits_form':detail_employee_benefits_form,
            'uq':{
                'create_link':str(reverse_lazy('benefits:create-benefit-scheme')),
            }
        }
        
        form = render_to_string('benefits/includes/benefit_scheme_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }

        return JsonResponse(response)

    def post(self, request):
        form_request = request.POST.copy()

        employees = form_request['employees[]'].split(',')
        benefits = form_request['benefits[]'].split(',')
        
        employees_data = [ get_object_or_404(Employees, hash_uuid = emp) for emp in employees ]
        benefits_data = [ get_object_or_404(Benefits, hash_uuid=ben) for ben in benefits ]

        del form_request['employees[]']
        del form_request['benefits[]']
        
        benefit_scheme_form = BenefitSchemeForm(form_request or None)
        detail_employee_benefits_form = DetailEmployeeBenefitsForm(form_request or None)

        if detail_employee_benefits_form.is_valid() and benefit_scheme_form.is_valid():
            try:
                benefit_scheme_data = benefit_scheme_form.cleaned_data
                detail_employee_benefits_data = detail_employee_benefits_form.cleaned_data
                
                # Add Additional Benefit Scheme Field to Database
                benefit_scheme_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_scheme_data['created_by'] = request.user
                benefit_scheme_data['updated_at'] = None
                benefit_scheme_data['updated_by'] = None
                benefit_scheme_data['deleted_at'] = None
                benefit_scheme_data['deleted_by'] = None
                
                created_benefit_scheme = BenefitScheme(**benefit_scheme_data)
                created_benefit_scheme.save()

                # Add Additional Detail Employee Benefits Field to Database
                detail_employee_benefits_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                detail_employee_benefits_data['created_by'] = request.user
                detail_employee_benefits_data['updated_at'] = None
                detail_employee_benefits_data['updated_by'] = None
                detail_employee_benefits_data['deleted_at'] = None
                detail_employee_benefits_data['deleted_by'] = None
                detail_employee_benefits_data['benefit_scheme_id'] = created_benefit_scheme
                del detail_employee_benefits_data['department']

                for employee in employees_data:
                    for benefit in benefits_data:
                        detail_employee_benefits_data['benefit_id'] = benefit
                        detail_employee_benefits_data['employee_id'] = employee

                        DetailEmployeeBenefits(**detail_employee_benefits_data).save()

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
                'toast_message':'Benefit Scheme Added Successfuly',
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

            for field, error_list in benefit_scheme_form.errors.items():
                errors[field] = error_list

            for field, error_list in detail_employee_benefits_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class UpdateBenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme', 'benefits.update_benefit_scheme']

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
    

    def get(self, request, benefit_scheme_uuid):
        benefit_scheme = get_object_or_404(BenefitScheme, hash_uuid=benefit_scheme_uuid)

        benefit_scheme_form = BenefitSchemeForm(instance=benefit_scheme)
        detail_employee_benefits_form = DetailEmployeeBenefitsForm()

        context = {
            'mode':'update',
            'benefit_scheme_form':benefit_scheme_form,
            'detail_employee_benefits_form':detail_employee_benefits_form,
            'modal_title':'update benefit scheme',
            'uq':{
                'hash': benefit_scheme_uuid,
                'update_link':str(reverse_lazy('benefits:update-benefit-scheme', args=["@@"])),
            }
        }
        
        form = render_to_string('benefits/includes/benefit_scheme_form.html', context, request=request)

        detail_benefits = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('benefit_id', flat=True)\
                                    .distinct()
        
        icons = '''
            <div class='d-flex justify-content-center'>
                <span class='update-benefit-detail btn text-warning w-100'>
                    <i class="bi bi-pencil"></i>
                </span>
                <span class='delete-benefit-detail btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        benefits_data = []
        for ben in detail_benefits:
            benefit = get_object_or_404(Benefits, id=ben)
            adjusted_benefit = BenefitAdjustments.objects\
                                    .filter(
                                        benefit_scheme_id = benefit_scheme,
                                        benefit_id = benefit,
                                        status = 1)\
                                    .distinct()\
                                    .order_by('-created_at')\
                                    .first()
            
            value = benefit.value
            if adjusted_benefit:
                value = adjusted_benefit.updated_value

            benefits_data.append({
                'uq_benefit': benefit.hash_uuid,
                'name': benefit.name,
                'description': benefit.description,
                'type_value': benefit.type_value,
                'value': value,
                'action': icons,
            })

        detail_employees = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('employee_id', flat=True)\
                                    .distinct()
        
        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-employee-detail btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        employees_data = []
        for emp in detail_employees:
            employee = get_object_or_404(Employees, id=emp)
            
            nik = employee.nik if employee.nik != '' else '-'
            nik_email = nik + '<br>' + employee.auth_user_id.email

            department = DepartmentMembers.objects.filter(employee_id = emp).values_list('department_id')
            department = Departments.objects.filter(id__in = department).values_list('name', flat=True)

            department_data = ''
            for dept in department:
                department_data += dept + '<br>'

            employees_data.append({
                'uq_emp': employee.hash_uuid,
                'nik_email':nik_email,
                'name': employee.name,
                'address': employee.address,
                'education': employee.education,
                'department': department_data,
                'join_date': employee.created_at.date().strftime("%d %B %Y"),
                'expired_at': employee.expired_at.strftime("%d %B %Y"),
                'status': employee.status,
                'action': trash_icon,
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            'benefits_data':benefits_data,
            'employees_data':employees_data,
        }

        return JsonResponse(response)

    def post(self, request, benefit_scheme_uuid):
        form_request = request.POST.copy()
        benefit_scheme = get_object_or_404(BenefitScheme, hash_uuid = benefit_scheme_uuid)
        benefit_scheme_form = BenefitSchemeForm(request.POST or None, instance=benefit_scheme)

        employees = form_request['employees[]'].split(',')
        benefits = form_request['benefits[]'].split(',')
        benefits_value = form_request['benefits_value[]'].split(',')

        # added, removed, reactivated employees = [(employee_id, benefit_id)], [(...)], [(...)]
        # Check if employees or benefits is empty
        added_employee_benefits, removed_employee_benefits, reactivated_employee_benefits = [], [], []
        frontend_benefit_data = {}

        if len("".join(employees)) != 0 and len("".join(benefits)) != 0:
            for emp_uuid in employees:
                for ben_uuid, value in zip(benefits, benefits_value):
                    emp = get_object_or_404(Employees, hash_uuid = emp_uuid)
                    ben = get_object_or_404(Benefits, hash_uuid = ben_uuid)
                    added_employee_benefits.append((emp.id, ben.id))

                    if value.isnumeric():
                        frontend_benefit_data[ben_uuid] = int(value)

        # Check Is There Any Inactive Detail Employee Benefits in user Input
        # If There is, then it's reactivated
        inactive_employee_benefits = DetailEmployeeBenefits.objects\
                                        .filter(benefit_scheme_id = benefit_scheme, status = 0)\
                                        .values_list('employee_id', 'benefit_id')
        
        for emp_ben in inactive_employee_benefits:
            try:
                added_employee_benefits.remove(emp_ben)
                reactivated_employee_benefits.append(emp_ben)
            except : pass

        # Check Is There Any Active Detail Employee Benefits in user Input
        # If There isn't , then it's removed
        active_employee_benefits = DetailEmployeeBenefits.objects\
                                        .filter(benefit_scheme_id = benefit_scheme, status = 1)\
                                        .values_list('employee_id', 'benefit_id')
        
        
        for emp_ben in active_employee_benefits:
            try: added_employee_benefits.remove(emp_ben)
            except : removed_employee_benefits.append(emp_ben)


        if benefit_scheme_form.is_valid():
            try:
                # Add Additional Field to Database
                benefit_scheme_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_scheme_form.cleaned_data['updated_by'] = request.user

                # Saving Data to Database
                benefit_scheme_form.save()

                if added_employee_benefits:
                    employee_benefits_data = {
                        'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                        'created_by': request.user,
                        'updated_at': None,
                        'updated_by': None,
                        'deleted_at': None,
                        'deleted_by': None,
                        'benefit_scheme_id': benefit_scheme,
                    }
                    
                    for emp_ben in added_employee_benefits:
                        # emp_ben = [employee.id, benefit.id]
                        benefit_object = get_object_or_404(Benefits, id=emp_ben[1])
                        employee_object = get_object_or_404(Employees, id=emp_ben[0])

                        employee_benefits_data['employee_id'] = employee_object
                        employee_benefits_data['benefit_id'] = benefit_object

                        DetailEmployeeBenefits(**employee_benefits_data).save()

                if removed_employee_benefits:
                    for emp_ben in removed_employee_benefits:
                        # emp_ben = [employee.id, benefit.id]
                        detail_emp_ben = get_object_or_404(DetailEmployeeBenefits, 
                                                            benefit_scheme_id = benefit_scheme, 
                                                            employee_id=emp_ben[0], 
                                                            benefit_id = emp_ben[1])
                        
                        detail_emp_ben.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        detail_emp_ben.deleted_by = request.user
                        detail_emp_ben.status = 0
                        detail_emp_ben.save()

                if reactivated_employee_benefits:
                    for emp_ben in reactivated_employee_benefits:
                        # emp_ben = [employee.id, benefit.id]
                        detail_emp_ben = get_object_or_404(DetailEmployeeBenefits, 
                                                            benefit_scheme_id = benefit_scheme, 
                                                            employee_id=emp_ben[0], 
                                                            benefit_id = emp_ben[1])

                        detail_emp_ben.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        detail_emp_ben.updated_by = request.user
                        detail_emp_ben.status = 1
                        detail_emp_ben.save()

                detail_employee_benefit_object = DetailEmployeeBenefits.objects\
                                                    .filter(benefit_scheme_id = benefit_scheme)\
                
                de_benefit_copy = detail_employee_benefit_object[:]

                for ben_uuid in frontend_benefit_data:
                    benefit_object = get_object_or_404(Benefits, hash_uuid = ben_uuid)
                    de_benefit = detail_employee_benefit_object.filter(benefit_id = benefit_object.id)

                    for detail_benefit in de_benefit:
                        if frontend_benefit_data[ben_uuid] != detail_benefit.benefit_id.value:
                            benefit_adjustment_object = BenefitAdjustments.objects.filter(
                                benefit_scheme_id = benefit_scheme,
                                employee_id=detail_benefit.employee_id,
                                benefit_id = detail_benefit.benefit_id,
                            )

                            if benefit_adjustment_object:
                                benefit_adjustment_object = benefit_adjustment_object.first()
                                benefit_adjustment_object.status = 1
                                benefit_adjustment_object.updated_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                                benefit_adjustment_object.updated_by = request.user
                                benefit_adjustment_object.updated_value = int(frontend_benefit_data[ben_uuid])
                                benefit_adjustment_object.save()

                            else:
                                benefit_adjustments_data = {
                                    'created_at': datetime.now(ZoneInfo('Asia/Bangkok')),
                                    'created_by': request.user,
                                    'updated_at': None,
                                    'updated_by': None,
                                    'deleted_at': None,
                                    'deleted_by': None,
                                    'benefit_scheme_id': benefit_scheme,
                                    'employee_id': detail_benefit.employee_id,
                                    'benefit_id': detail_benefit.benefit_id,
                                    'updated_value': int(frontend_benefit_data[ben_uuid]),
                                }

                                BenefitAdjustments(**benefit_adjustments_data).save()

                            # remove copy from de_benefit_copy
                            de_benefit_copy = de_benefit_copy.exclude(id = detail_benefit.id)
                
                for detail_benefit in de_benefit_copy:
                    benefit_adjustment_object = BenefitAdjustments.objects\
                                                    .filter(
                                                        benefit_scheme_id = benefit_scheme, 
                                                        employee_id=detail_benefit.employee_id, 
                                                        benefit_id = detail_benefit.benefit_id)\
                                                    .first()
                    
                    if benefit_adjustment_object:
                        benefit_adjustment_object.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
                        benefit_adjustment_object.deleted_by = request.user
                        benefit_adjustment_object.status = 0
                        benefit_adjustment_object.save()


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
                'toast_message':'Benefit Scheme Updated Successfuly',
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
            for field, error_list in benefit_scheme_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailBenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme']

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

    def get(self, request, benefit_scheme_uuid):
        benefit_scheme = get_object_or_404(BenefitScheme, hash_uuid=benefit_scheme_uuid)

        benefit_scheme_form = BenefitSchemeForm(instance=benefit_scheme)
        detail_employee_benefits_form = DetailEmployeeBenefitsForm()

        for key in benefit_scheme_form.fields:
            benefit_scheme_form.fields[key].widget.attrs['disabled'] = True
            benefit_scheme_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'benefit_scheme_form':benefit_scheme_form,
            'detail_employee_benefits_form':detail_employee_benefits_form,
            'modal_title':'view benefit scheme',
        }
        
        form = render_to_string('benefits/includes/benefit_scheme_form.html', context, request=request)

        detail_benefits = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('benefit_id', flat=True)\
                                    .distinct()
        
        benefits_data = []
        for ben in detail_benefits:
            benefit = get_object_or_404(Benefits, id=ben)
            adjusted_benefit = BenefitAdjustments.objects\
                                    .filter(
                                        benefit_scheme_id = benefit_scheme,
                                        benefit_id = benefit,
                                        status = 1)\
                                    .distinct()\
                                    .order_by('-created_at')\
                                    .first()
            
            value = benefit.value
            if adjusted_benefit:
                value = adjusted_benefit.updated_value

            benefits_data.append({
                'uq_benefit': benefit.hash_uuid,
                'name': benefit.name,
                'description': benefit.description,
                'type_value': benefit.type_value,
                'value': value,
                'action': '',
            })

        detail_employees = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('employee_id', flat=True)\
                                    .distinct()
        

        employees_data = []
        for emp in detail_employees:
            employee = get_object_or_404(Employees, id=emp)
            
            department = DepartmentMembers.objects.filter(employee_id = emp).values_list('department_id')
            department = Departments.objects.filter(id__in = department).values_list('name', flat=True)

            department_data = ''
            for dept in department:
                department_data += dept + '<br>'

            nik = employee.nik if employee.nik != '' else '-'
            nik_email = nik + '<br>' + employee.auth_user_id.email

            employees_data.append({
                'uq_emp': employee.hash_uuid,
                'nik_email':nik_email,
                'name': employee.name,
                'address': employee.address,
                'education': employee.education,
                'department': department_data,
                'join_date': employee.created_at.date().strftime("%d %B %Y"),
                'expired_at': employee.expired_at.strftime("%d %B %Y"),
                'status': employee.status,
                'action':'',
            })

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
            'benefits_data':benefits_data,
            'employees_data':employees_data,
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    

class DeleteBenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme', 'benefits.delete_benefit_scheme']

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

    def post(self, request, benefit_scheme_uuid):
        benefit_scheme = get_object_or_404(BenefitScheme, hash_uuid=benefit_scheme_uuid)
        benefit_scheme.status = 0
        benefit_scheme.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        benefit_scheme.deleted_by = request.user
        benefit_scheme.save()

        response = {
            'success': True, 
            'toast_message':'Benefit Scheme Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class BenefitSchemeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme']

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
            'title':'Benefits Scheme',
        }

        return render(request, 'benefits/benefit_scheme.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class AddBenefitDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme']

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
        benefit = request.POST['benefit']
        try:
            if uuid.UUID(benefit, version=4):
                benefit = get_object_or_404(Benefits, hash_uuid=benefit)

                icons = '''
                    <div class="d-flex justify-content-center">
                        <span class='update-benefit-detail btn text-warning w-100'>
                            <i class="bi bi-pencil"></i>
                        </span>
                        <span class="delete-benefit-detail btn text-danger w-100">
                            <i class="bi bi-trash"></i>
                        </span>
                    </div>
                '''

                benefit_data = {
                    'uq_benefit':benefit.hash_uuid,
                    'name': benefit.name,
                    'description': benefit.description,
                    'type_value': benefit.type_value,
                    'value': benefit.value,
                    'action':icons,
                }

                response = {
                    'success':True,
                    'benefit_data':benefit_data,
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
        
class ShowEmployeesDepartmentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['benefits.read_benefit_scheme']

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
        department = request.POST['department']
        try:
            if uuid.UUID(department, version=4):
                department = get_object_or_404(Departments, hash_uuid=department)
                employees = DepartmentMembers.objects.filter(department_id = department)

                add_icon = '''
                    <div class="d-flex justify-content-center">
                        <span class="add-employee-detail btn text-success w-100">
                            <i class="fa-solid fa-plus"></i>
                        </span>
                    </div>
                '''

                employees_data = []
                for emp in employees:
                    nik = emp.employee_id.nik if emp.employee_id.nik != '' else '-'
                    nik_email = nik + '<br>' + emp.employee_id.auth_user_id.email

                    department = DepartmentMembers.objects.filter(employee_id = emp.employee_id).values_list('department_id')
                    department = Departments.objects.filter(id__in = department).values_list('name', flat=True)

                    department_data = ''
                    for dept in department:
                        department_data += dept + '<br>'

                    employees_data.append({
                        'uq_emp':emp.employee_id.hash_uuid,
                        'nik_email':nik_email,
                        'name': emp.employee_id.name,
                        'address': emp.employee_id.address,
                        'education': emp.employee_id.education,
                        'department': department_data,
                        'join_date': emp.employee_id.created_at.date().strftime("%d %B %Y"),
                        'expired_at': emp.employee_id.expired_at.strftime("%d %B %Y"),
                        'status': emp.employee_id.status,
                        'action':add_icon,
                    })

                response = {
                    'success':True,
                    'employees_data':employees_data,
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
        

class ListPTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request):
        context = {
            'view_link':str(reverse_lazy('benefits:detail-ptkp-type', args=["@@"])),
            'update_link': str(reverse_lazy('benefits:update-ptkp-type', args=["@@"])),
            'delete_link':str(reverse_lazy('benefits:delete-ptkp-type', args=["@@"])),
        }

        ptkp_object = PTKPType.objects.all()
        ptkp_type_data = []

        for ptkp in ptkp_object:
            context['hash'] = ptkp.hash_uuid
            form_action = render_to_string('benefits/includes/ptkp_type_form_action_button.html', context, request=request)
            
            ptkp_type_data.append({
                'name':ptkp.name,
                'value':ptkp.value,
                'status':ptkp.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'ptkp_type_data': ptkp_type_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreatePTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request):
        ptkp_type_form = PTKPTypeForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create ptkp type',
            'ptkp_type_form':ptkp_type_form,
            'uq':{
                'create_link':str(reverse_lazy('benefits:create-ptkp-type')),
            }
        }
        
        form = render_to_string('benefits/includes/ptkp_type_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        return JsonResponse(response)

    def post(self, request):
        ptkp_type_form = PTKPTypeForm(request.POST or None)

        if ptkp_type_form.is_valid():
            
            try:
                ptkp_type_data = ptkp_type_form.cleaned_data

                # Add Additional PTKP Type Field to Database
                ptkp_type_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                ptkp_type_data['created_by'] = request.user
                ptkp_type_data['updated_at'] = None
                ptkp_type_data['updated_by'] = None
                ptkp_type_data['deleted_at'] = None
                ptkp_type_data['deleted_by'] = None

                PTKPType(**ptkp_type_data).save()

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
                'toast_message':'PTKP Type Added Successfuly',
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

            for field, error_list in ptkp_type_form.errors.items():
                errors[field] = error_list

            
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdatePTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request, ptkp_type_uuid):
        ptkp = get_object_or_404(PTKPType, hash_uuid=ptkp_type_uuid)
        ptkp_type_form = PTKPTypeForm(instance=ptkp)

        context = {
            'mode':'update',
            'ptkp_type_form':ptkp_type_form,
            'modal_title':'update ptkp type',
            'uq':{
                'hash': ptkp_type_uuid,
                'update_link':str(reverse_lazy('benefits:update-ptkp-type', args=["@@"])),
            }
        }
        
        form = render_to_string('benefits/includes/ptkp_type_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }

        return JsonResponse(response)

    def post(self, request, ptkp_type_uuid):
        ptkp = get_object_or_404(PTKPType, hash_uuid=ptkp_type_uuid)
        ptkp_type_form = PTKPTypeForm(request.POST or None, instance=ptkp)

        if ptkp_type_form.is_valid():
            try:
                # Add Additional Field to Database
                ptkp_type_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                ptkp_type_form.cleaned_data['updated_by'] = request.user

                # Saving PTKP Type to Database
                ptkp_type_form.save()

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
                'toast_message':'PTKP Type Updated Successfuly',
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
            for field, error_list in ptkp_type_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailPTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request, ptkp_type_uuid):
        ptkp = get_object_or_404(Benefits, hash_uuid=ptkp_type_uuid)
        ptkp_type_form = PTKPTypeForm(instance=ptkp)
        

        for key in ptkp_type_form.fields:
            ptkp_type_form.fields[key].widget.attrs['disabled'] = True
            ptkp_type_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'ptkp_type_form':ptkp_type_form,
            'modal_title':'view ptkp type',
        }
        
        form = render_to_string('benefits/includes/ptkp_type_form.html', context, request=request)

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

class DeletePTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request, ptkp_type_uuid):
        ptkp = get_object_or_404(PTKPType, hash_uuid=ptkp_type_uuid)
        ptkp.status = 0
        ptkp.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        ptkp.deleted_by = request.user
        ptkp.save()

        response = {
            'success': True, 
            'toast_message':'PTKP Type Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class PTKPTypeView(LoginRequiredMixin, View):
    login = '/login/'

    def get(self, request):
        context = {
            'title':'PTKP Type',
        }

        return render(request, 'benefits/ptkp_type.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))