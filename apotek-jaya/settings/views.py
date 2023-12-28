from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from .models import Settings
from .forms import SettingsForm

class ListSettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['settings.read_settings']

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
            'view_link':str(reverse_lazy('settings:detail-settings')),
            'update_link': str(reverse_lazy('settings:update-settings')),
        }

        settings_object = Settings.objects.all()
        settings_data = []

        if len(settings_object) > 0:
            settings_object = settings_object[0]

            context['hash'] = settings_object.hash_uuid
            form_action = render_to_string('settings/includes/settings_form_action_button.html', context, request=request)
            settings_data.append({
                'overtime_rate': settings_object.overtime_rate,
                'lembur_rate':settings_object.lembur_rate,
                'uq': form_action, 
            })

        response = {
            'success':True,
            'settings_data': settings_data
        }

        return JsonResponse(response)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))

class CreateSettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['settings.read_settings', 'settings.create_settings']

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
        settings_form = SettingsForm()

        context = {
            'success':True,
            'mode':'create',
            'modal_title':'create settings',
            'settings_form':settings_form,
            'uq':{
                'create_link':str(reverse_lazy('settings:create-settings')),
            }
        }
        
        form = render_to_string('settings/includes/settings_form.html', context, request=request)
        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }
        
        return JsonResponse(response)

    def post(self, request):
        settings_form = SettingsForm(request.POST or None)
        settings_object = Settings.objects.all()

        if settings_form.is_valid() and len(settings_object) == 0:
            try:
                settings_data = settings_form.cleaned_data

                Settings(**settings_data).save()

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
                'toast_message':'Settings Added Successfuly',
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

            for field, error_list in settings_form.errors.items():
                errors[field] = error_list

            print('errors')
            print(errors)

            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)

class UpdateSettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['settings.read_settings', 'settings.update_settings']

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
        setting = Settings.objects.all().first()
        settings_form = SettingsForm(instance=setting)

        context = {
            'mode':'update',
            'settings_form':settings_form,
            'modal_title':'update settings',
            'uq':{
                'update_link':str(reverse_lazy('settings:update-settings')),
            }
        }
        
        form = render_to_string('settings/includes/settings_form.html', context, request=request)

        response = {
            'success':True,
            'form': form,
            'is_view_only': False,
        }

        return JsonResponse(response)

    def post(self, request):
        setting = Settings.objects.all().first()
        settings_form = SettingsForm(request.POST or None, instance=setting)

        if settings_form.is_valid():
            try:
                settings_form.save()

            except Exception as e:
                print('error')
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
                'toast_message':'Settings Updated Successfuly',
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
            for field, error_list in settings_form.errors.items():
                errors[field] = error_list

            print('errors')
            print(errors)
            response = {
                'success': False, 
                'errors': errors, 
                'modal_messages':modal_messages,
                'toast_message':'Please review the form and correct any errors before resubmitting',
                'is_close_modal':False
            }

            return JsonResponse(response)


class DetailSettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['settings.read_settings']

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
        setting = Settings.objects.all().first()
        settings_form = SettingsForm(instance=setting)

        for key in settings_form.fields:
            settings_form.fields[key].widget.attrs['disabled'] = True
            settings_form.fields[key].widget.attrs['placeholder'] = ''

        context = {
            'mode':'view',
            'settings_form':settings_form,
            'modal_title':'view settings',
        }
        
        form = render_to_string('settings/includes/settings_form.html', context, request=request)

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
    
class SettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ['settings.read_settings']

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
        settings_object = Settings.objects.all()
        is_need_create = True if len(settings_object) <= 0 else False
        
        context = {
            'title':'Settings',
            'is_need_create': is_need_create,
        }

        return render(request, 'settings/settings.html', context)

    def post(self, request):
        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('main_app:home'))

        return redirect(reverse_lazy('main_app:login'))