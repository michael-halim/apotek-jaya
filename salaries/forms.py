from django import forms
from django.contrib.auth.models import Group

from .models import PayrollPeriods

class PayrollPeriodsForm(forms.ModelForm):
    def clean_name(self):
        print('Enter Clean Payroll Periods Name')
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        errors = []

        if name is None:
            errors.append('Payroll Period Name Cannot be Empty')

        elif len(name) <= 0:
            errors.append('Payroll Period Name Cannot be Empty')

        elif len(name) > 200:
            errors.append('Payroll Period Name Cannot be Longer Than 200 Letters')

        if errors:
            raise forms.ValidationError(errors)

        return name
    
    def clean_description(self):
        print('Enter Clean Payroll Period Description')
        cleaned_data = super().clean()
        description = cleaned_data.get('description')
        errors = []

        if description is None:
            description = ''

        elif len(description) > 400:
            errors.append('Payroll Period Description Cannot be Longer Than 400 Characters')

        if errors:
            raise forms.ValidationError(errors)

        return description
    
    def clean_status(self):
        print('Enter Clean Status')
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        errors = []
        if status is None:
            status = 1

        else:
            if int(status) > 3:
                errors.append('Status is Not Valid')

        if errors:
            raise forms.ValidationError(errors)

        return status
    
    def clean_end_at(self):
        print('Enter Clean End At')
        cleaned_data = super().clean()
        end_at = cleaned_data.get('end_at')
        errors = []

        if end_at is None:
            errors.append('Payroll End At Cannot be Empty')

        else:
            start_at = cleaned_data.get('start_at')
            
            if end_at < start_at:
                errors.append('End At Cannot Less Than Start At')

        if errors:
            raise forms.ValidationError(errors)

        return end_at

    class Meta:
        model = PayrollPeriods
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Payroll Period Name is Required'
            },
            'start_at':{
                'required': 'Start At is Required'
            },
            'end_at':{
                'required': 'End At is Required'
            }
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Payroll Period Name',
                'required': True,
                'id':'name',
                
            }),
            'start_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder':'Enter Payroll Period Start',
                'required': False,
                'id':'start_at',
            }),
            'end_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder':'Enter Payroll Period End',
                'required': False,
                'id':'end_at',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Payroll Period Description',
                'required': False,
                'id':'description',
                
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'name': 'Payroll Period Name',
            'status': 'Status',
        }

