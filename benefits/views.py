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

from departments.models import DepartmentMembers, Departments

from .forms import BenefitSchemeForm, BenefitsForm, DetailEmployeeBenefitsForm
from .models import BenefitScheme, Benefits, DetailEmployeeBenefits

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
            form_action = render_to_string('benefits/includes/benefits_form_action_button.html', context, request=request)
            
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
        
        form = render_to_string('benefits/includes/benefits_form.html', context, request=request)
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
        
        form = render_to_string('benefits/includes/benefits_form.html', context, request=request)

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
    

class ListBenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'

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
        pass

class CreateBenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'

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
        print('before deleted')
        print(form_request)

        employees = form_request['employees[]'].split(',')
        benefits = form_request['benefits[]'].split(',')
        
        employees_data = [ get_object_or_404(Employees, hash_uuid = emp) for emp in employees ]
        benefits_data = [ get_object_or_404(Benefits, hash_uuid=ben) for ben in benefits ]


        del form_request['employees[]']
        del form_request['benefits[]']
        
        print('after deleted')
        print(form_request)

        benefit_scheme_form = BenefitSchemeForm(form_request or None)
        detail_employee_benefits_form = DetailEmployeeBenefitsForm(form_request or None)

        if detail_employee_benefits_form.is_valid() and benefit_scheme_form.is_valid():
            print('Benefits Form is Valid')
            
            try:
                print('SAVING TO DB')
                benefit_scheme_data = benefit_scheme_form.cleaned_data
                detail_employee_benefits_data = detail_employee_benefits_form.cleaned_data
                
                benefit_scheme_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                benefit_scheme_data['created_by'] = request.user
                benefit_scheme_data['updated_at'] = None
                benefit_scheme_data['updated_by'] = None
                benefit_scheme_data['deleted_at'] = None
                benefit_scheme_data['deleted_by'] = None
                
                created_benefit_scheme = BenefitScheme(**benefit_scheme_data)
                created_benefit_scheme.save()

                print('benefit_scheme_data')
                print(benefit_scheme_data)

                # Add Additional Benefits Field to Database
                detail_employee_benefits_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                detail_employee_benefits_data['created_by'] = request.user
                detail_employee_benefits_data['updated_at'] = None
                detail_employee_benefits_data['updated_by'] = None
                detail_employee_benefits_data['deleted_at'] = None
                detail_employee_benefits_data['deleted_by'] = None
                detail_employee_benefits_data['benefit_scheme_id'] = created_benefit_scheme
                del detail_employee_benefits_data['department']

                print(detail_employee_benefits_data)

                print('employees_data')
                print(employees_data)

                print('benefits_data')
                print(benefits_data)

                for employee in employees_data:
                    for benefit in benefits_data:
                        detail_employee_benefits_data['benefit_id'] = benefit
                        detail_employee_benefits_data['employee_id'] = employee

                        DetailEmployeeBenefits(**detail_employee_benefits_data).save()

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


class UpdateBenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'


    def get(self, request, benefit_scheme_uuid):
        benefit_scheme = get_object_or_404(BenefitScheme, hash_uuid=benefit_scheme_uuid)

        benefit_scheme_form = BenefitSchemeForm(instance=benefit_scheme)
        detail_employee_benefits_form = DetailEmployeeBenefitsForm()

        context = {
            'mode':'update',
            'benefit_scheme_form':benefit_scheme_form,
            'detail_employee_benefits_form':detail_employee_benefits_form,
            'modal_title':'view benefit scheme',
        }
        
        form = render_to_string('benefits/includes/benefit_scheme_form.html', context, request=request)

        detail_benefits = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('benefit_id', flat=True)\
                                    .distinct()
        
        print('detail_benefits')
        print(detail_benefits)

        trash_icon = '''
            <div class='d-flex justify-content-center'>
                <span class='delete-benefit-detail btn text-danger w-100'>
                    <i class="bi bi-trash"></i>
                </span>
            </div>
        '''

        benefits_data = []
        for ben in detail_benefits:
            benefit = get_object_or_404(Benefits, id=ben)
            benefits_data.append({
                'uq_benefit': benefit.hash_uuid,
                'name': benefit.name,
                'description': benefit.description,
                'type_value': benefit.type_value,
                'value': benefit.value,
                'action': trash_icon,
            })

        detail_employees = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('employee_id', flat=True)\
                                    .distinct()
        
        print('detail_employees')
        print(detail_employees)

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

    def post(self, request):
        pass

class DetailBenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'


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
        
        print('detail_benefits')
        print(detail_benefits)

        benefits_data = []
        for ben in detail_benefits:
            benefit = get_object_or_404(Benefits, id=ben)
            benefits_data.append({
                'uq_benefit': benefit.hash_uuid,
                'name': benefit.name,
                'description': benefit.description,
                'type_value': benefit.type_value,
                'value': benefit.value,
                'action': '',
            })

        detail_employees = DetailEmployeeBenefits.objects\
                                    .filter(benefit_scheme_id=benefit_scheme, status=1)\
                                    .values_list('employee_id', flat=True)\
                                    .distinct()
        
        print('detail_employees')
        print(detail_employees)

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
        pass

class DeleteBenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'


    def get(self, request):
        pass

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

class BenefitSchemeView(LoginRequiredMixin, View):
    login_url = '/login/'


    def get(self, request):
        context = {
            'title':'Benefits Scheme',
        }

        return render(request, 'benefits/benefit_scheme.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))
    
class AddBenefitDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        pass

    def post(self, request):
        print(request.POST)
        benefit = request.POST['benefit']
        try:
            if uuid.UUID(benefit, version=4):
                print('WORKS')
                benefit = get_object_or_404(Benefits, hash_uuid=benefit)

                trash_icon = '''
                    <div class="d-flex justify-content-center">
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
                    'action':trash_icon,
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
        
class ShowEmployeesDepartmentView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

    def post(self, request):
        print(request.POST)

        department = request.POST['department']
        try:
            if uuid.UUID(department, version=4):
                print('WORKS')
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