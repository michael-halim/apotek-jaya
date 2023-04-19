from django import forms

from .models import Departments

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

class DepartmentsForm(forms.ModelForm):
    def clean_name(self):
        print('Enter Clean Department Name')
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        errors = []

        if name is None:
            errors.append('Department Name Cannot be Empty')

        elif len(name) <= 0:
            errors.append('Department Name Cannot be Empty')

        elif len(name) > 200:
            errors.append('Department Name Cannot be Longer Than 200 Letters')

        if errors:
            raise forms.ValidationError(errors)

        return name

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

    class Meta:
        model = Departments
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Department Name is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Department Name',
                'required': True,
                'id':'name',
                
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'name': 'Department Name',
            'status': 'Status',
        }