from django import forms
from django.contrib.auth.models import Group

from employees.models import Employees

from .models import Overtimes, OvertimeUsers


class OvertimesForm(forms.ModelForm):
    def clean_name(self):
        print('Enter Clean Overtimes Name')
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        errors = []

        if name is None:
            errors.append('Benefit Name Cannot be Empty')

        elif len(name) <= 0:
            errors.append('Benefit Name Cannot be Empty')

        elif len(name) > 200:
            errors.append('Benefit Name Cannot be Longer Than 200 Letters')

        if errors:
            raise forms.ValidationError(errors)

        return name
    
    def clean_description(self):
        print('Enter Clean Overtimes Description')
        cleaned_data = super().clean()
        description = cleaned_data.get('description')
        errors = []

        if description is None:
            description = ''

        elif len(description) > 400:
            errors.append('Department Name Cannot be Longer Than 400 Characters')

        if errors:
            raise forms.ValidationError(errors)

        return description
    

    class Meta:
        model = Overtimes
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Benefit Name is Required'
            },
            'start_at': {
                'required': 'Start At is Required'
            },
            'end_at': {
                'required': 'End At is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Overtime Name',
                'required': True,
                'id':'name',
                
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':'Enter Overtime Description',
                'required': False,
                'id':'description',
                
            }),
            'start_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True,
                'id':'start_at',
            }),

            'end_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True,
                'id':'end_at',
            }),

            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'name': 'Overtime Name',
            'start_at': 'Start At',
            'end_at': 'End At',
            'status': 'Status',
        }

class OvertimeUsersForm(forms.ModelForm):
    employee_id = forms.ModelChoiceField(
                    queryset = Employees.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'employee_id',
                        }),
                    required=True,
                    label='Employees',
                    to_field_name='hash_uuid')
    
    class Meta:
        model = OvertimeUsers
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'status', 'overtime_id']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            
        }
        labels = {
            
        }