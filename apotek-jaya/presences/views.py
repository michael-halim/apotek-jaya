import re
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .models import Presences
from .forms import PresenceBulkInputForm, PresencesForm
from employees.models import Employees

from datetime import datetime
from zoneinfo import ZoneInfo
import openpyxl

class ListPresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences']

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
            'view_link':str(reverse_lazy('presences:detail-presences', args=["@@"])),
            'update_link': str(reverse_lazy('presences:update-presences', args=["@@"])),
            'delete_link':str(reverse_lazy('presences:delete-presences', args=["@@"])),
        }

        presences_object = Presences.objects.all()
        presences_data = []

        for presence in presences_object:
            context['hash'] = presence.hash_uuid
            form_action = render_to_string('presences/includes/presences_form_action_button.html', context, request=request)
            employee = get_object_or_404(Employees, id=presence.employee_id.id)
            nik = employee.nik if employee.nik else '-'
            nik = '<span class="badge bg-success">{nik}</span>'.format(nik=nik)
            nik_name = nik + '<br>' + employee.name
            start_at = presence.start_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%H:%M") if presence.start_at is not None else '-'
            end_at = presence.end_at.astimezone(ZoneInfo('Asia/Bangkok')).strftime("%H:%M") if presence.end_at is not None else '-'
            presences_data.append({
                'nik_name':nik_name,
                'date': presence.date.strftime("%d %B %Y"),
                'start_at': start_at,
                'end_at': end_at,
                'status':presence.status,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'presences_data': presences_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreatePresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences', 'presences.create_presences']

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
        presences_form = PresencesForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create presences',
            'presences_form':presences_form,
            'uq':{
                'create_link':str(reverse_lazy('presences:create-presences')),
            }
        }
        
        form = render_to_string('presences/includes/presences_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
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

        if request.POST['employee_id'] == '' or len(request.POST['employee_id']) == 0:
            failed_response['toast_message'] = 'Must Select Employee'
            return JsonResponse(failed_response)

        start_at = datetime.strptime(request.POST['start_at'], '%Y-%m-%dT%H:%M').replace(hour=0, minute=0, second=0)
        end_at = datetime.strptime(request.POST['start_at'], '%Y-%m-%dT%H:%M').replace(hour=23, minute=59, second=59)
        
        presences_form = PresencesForm(request.POST or None)
        employee = get_object_or_404(Employees, hash_uuid=request.POST['employee_id'])
        
        presence_object = Presences.objects.filter(employee_id=employee, 
                                                   start_at__gte=start_at, 
                                                    end_at__lte=end_at,
                                                   status=1)

        if presence_object.count() > 0:
            failed_response['toast_message'] = 'Employee Already Has an Active Presence'
            return JsonResponse(failed_response)

        if presences_form.is_valid():
            if presences_form.cleaned_data['start_at'] > presences_form.cleaned_data['end_at']:         
                failed_response['toast_message'] = 'Start At Cannot Be Greater Than End At'
                return JsonResponse(failed_response)

            if presences_form.cleaned_data['start_at'].date() != presences_form.cleaned_data['end_at'].date():
                failed_response['toast_message'] = 'Start At And End At Must Be On The Same Date'
                return JsonResponse(failed_response)
            
            try:
                presences_data = presences_form.cleaned_data

                presences_data['created_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                presences_data['created_by'] = request.user
                presences_data['updated_at'] = None
                presences_data['updated_by'] = None

                Presences(**presences_data).save()

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
                'toast_message':'Presence Added Successfuly',
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

            for field, error_list in presences_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdatePresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences', 'presences.update_presences']

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
    
    def get(self, request, presence_uuid):
        presence_object = get_object_or_404(Presences, hash_uuid=presence_uuid)

        initial_data = {
            'employee_id':presence_object.employee_id,
        }

        presences_form = PresencesForm(instance=presence_object, initial=initial_data)

        presences_form.fields['employee_id'].widget.attrs['disabled'] = True
        presences_form.fields['employee_id'].widget.attrs['placeholder'] = ''

        context = {
            'mode':'update',
            'presences_form':presences_form,
            'modal_title':'update presences',
            'uq':{
                'hash': presence_uuid,
                'update_link':str(reverse_lazy('presences:update-presences', args=["@@"])),
            }
        }
        
        form = render_to_string('presences/includes/presences_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': True,
        }

        return JsonResponse(response)

    def post(self, request, presence_uuid):
        employee = get_object_or_404(Employees, hash_uuid=request.POST['employee_id'] )
        presence_object = get_object_or_404(Presences, hash_uuid=presence_uuid)
        presences_form = PresencesForm(request.POST or None, instance=presence_object)

        failed_response = {
            'success': False, 
            'errors': [], 
            'modal_messages':[],
            'is_close_modal':False,
        }

        if presence_object.employee_id != employee:
            failed_response['toast_message'] = 'You\'re not allowed to change employee'
            return JsonResponse(response)
        
        start_at = datetime.strptime(request.POST['start_at'], '%Y-%m-%dT%H:%M').replace(hour=0, minute=0, second=0)
        end_at = datetime.strptime(request.POST['start_at'], '%Y-%m-%dT%H:%M').replace(hour=23, minute=59, second=59)
        
        presence_object_count = Presences.objects.filter(employee_id=employee, 
                                                   start_at__gte=start_at, 
                                                    end_at__lte=end_at,
                                                   status=1)
        
        if presence_object_count.count() > 0:
            failed_response['toast_message'] = 'Employee Already Has an Active Presence'
            return JsonResponse(failed_response)
        
        if presences_form.is_valid():
            try:

                # Add Additional Field to Database
                presences_form.cleaned_data['updated_at'] = datetime.now(ZoneInfo('Asia/Bangkok'))
                presences_form.cleaned_data['updated_by'] = request.user

                # Saving Presences to Database
                presences_form.save()

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
                'toast_message':'Presence Updated Successfuly',
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
            for field, error_list in presences_form.errors.items():
                errors[field] = error_list

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class DetailPresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences']

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
    
    def get(self, request, presence_uuid):
        presence_object = get_object_or_404(Presences, hash_uuid=presence_uuid)
        
        initial_data = {
            'employee_id':presence_object.employee_id,
        }

        presences_form = PresencesForm(instance=presence_object, initial=initial_data)
        for key in presences_form.fields:
            presences_form.fields[key].widget.attrs['disabled'] = True
            presences_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'presences_form':presences_form,
            'modal_title':'view presences',
        }
        
        form = render_to_string('presences/includes/presences_form.html', context, request=request)

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

class DeletePresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences', 'presences.delete_presences']

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

    def post(self, request, presence_uuid):
        presence = get_object_or_404(Presences, hash_uuid=presence_uuid)
        presence.status = 0
        presence.deleted_at = datetime.now(ZoneInfo('Asia/Bangkok'))
        presence.deleted_by = request.user
        presence.save()

        response = {
            'success': True, 
            'toast_message':'Presence Deactivated Successfuly',
            'is_close_modal':True
        }

        return JsonResponse(response)

class PresencesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences']

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
            'title':'Presences',
        }

        return render(request, 'presences/presences.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreatePresencesBulkView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['presences.read_presences']

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
        presences_bulk_form = PresenceBulkInputForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create presences',
            'presences_bulk_form':presences_bulk_form,
            'uq':{
                'create_link':str(reverse_lazy('presences:create-presences-bulk')),
            }
        }
        
        form = render_to_string('presences/includes/presences_bulk_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
            
        }
        
        return JsonResponse(response)

    def post(self, request):    
        if request.method == 'POST' and request.FILES['file_upload']:
            failed_response = {
                'success': False,
                'errors': [],
                'modal_messages':[],
                'is_close_modal':False,
            }

            uploaded_file = request.FILES['file_upload']
            if not uploaded_file.name.endswith('.xlsx') and not uploaded_file.name.endswith('.xls'):
                failed_response['toast_message'] = 'File Must Be in .xlsx or .xls Format'
                return JsonResponse(failed_response)
            
            # Add Current NIK and Line in Excel Code for Error Message
            current_line = None
            try:
                workbook = openpyxl.load_workbook(uploaded_file)
                sheet = workbook.active
                
                excel_data = []
                dates = []
                for co, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                    print('co')
                    print(co)
                    print('row')
                    print(row)
                    
                    if co == 1:
                        string_row = ' '.join(str(x) for x in row)
                        dates = re.findall(r'\d+\/\d+\/\d+', string_row)
                        continue

                    if co == 2:
                        continue
                    
                    print('dates')
                    print(dates)
                    current_line = co
                    nik = row[1]
                    for co, i in enumerate(range(7, 7 + (len(dates) * 2), 2)):
                        time_pattern = r'^\d{2}:\d{2}$'
                        start, end = row[i].strip() if row[i] is not None else '', row[i+1].strip() if row[i+1] is not None else ''
                        
                        start = None if start == '' else start
                        end = None if end == '' else end
                        if start is not None and end is not None:
                            if not re.match(time_pattern, start) or not re.match(time_pattern, end) and (start != '' or end != ''):
                                failed_response['toast_message'] = 'error in line {line}. Doesn\'t have hh:mm pattern'.format(line=co)
                                return JsonResponse(failed_response)

                        excel_data.append({
                            'nik':nik,
                            'date': datetime.strptime(dates[co], '%d/%m/%Y'),
                            'start_at': datetime.strptime(str(dates[co]) + ' ' +  str(start), '%d/%m/%Y %H:%M') if start is not None else None,
                            'end_at': datetime.strptime(str(dates[co]) + ' ' + str(end), '%d/%m/%Y %H:%M') if end is not None else None,
                        })

                presence_data = []
                for co, row in enumerate(excel_data, start=1):
                    employee =  Employees.objects.filter(nik=row['nik']).first()
                    if employee is None:
                        failed_response['toast_message'] = 'Employee with NIK {nik} in line {line} Not Found'.format(nik = row['nik'], line=co)
                        return JsonResponse(failed_response)


                    presence_data.append(Presences(
                        employee_id=employee,
                        date= row['date'],
                        start_at=row['start_at'],
                        end_at=row['end_at'],
                        status=1,
                        created_at=datetime.now(ZoneInfo('Asia/Bangkok')),
                        created_by=request.user,
                        updated_at=None,
                        updated_by=None,
                    ))
                
                # Create Bulk Data
                Presences.objects.bulk_create(presence_data)

                response = {
                    'success':True,
                    'toast_message':'Presence Created Successfuly',
                    'is_close_modal': True,
                }

                return JsonResponse(response)
            
            except ValueError as ve:
                print('ve')
                print(ve)
                response = {
                    'success':False,
                    'toast_message':'There are error in line {line}'.format(line=current_line),
                    'is_close_modal': True,
                }

                return JsonResponse(response)
        
        failed_response = {
            'success': False,
            'errors': [],
            'toast_message': 'File Upload Failed',
            'modal_messages':[],
            'is_close_modal':False,
        }

        return JsonResponse(failed_response)