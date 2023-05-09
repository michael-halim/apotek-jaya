from django import forms
from django.contrib.auth.models import Group

from .models import Benefits

class BenefitsForm(forms.ModelForm):

    def clean_name(self):
        print('Enter Clean Benefits Name')
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
    
    def clean_type_value(self):
        print('Enter Clean Type Value')
        cleaned_data = super().clean()
        type_value = cleaned_data.get('type_value')
        errors = []

        if type_value is None:
            errors.append('Benefit Name Cannot be Empty')

        else:
            if type_value not in ['+', '-']:
                errors.append('Type Value Can Only be + or -')

        if errors:
            raise forms.ValidationError(errors)

        return type_value
    
    def clean_description(self):
        print('Enter Clean Benefits Description')
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
    
    def clean_value(self):
        print('Enter Clean Benefits Value')
        cleaned_data = super().clean()
        value = cleaned_data.get('value')

        errors = []

        if value is None:
            errors.append('Value Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        print(value)
        return value

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
        model = Benefits
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Benefit Name is Required'
            },
            'type_value': {
                'required': 'Type Value is Required'
            },
            'value': {
                'required': 'Value is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Name',
                'required': True,
                'id':'name',
                
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Description Name',
                'required': False,
                'id':'description',
                
            }),
            'type_value': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id':'type_value',

            }, choices=[('+', '+'), ('-', '-')]),

            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Value',
                'required': True,
                'id':'value',
                
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'name': 'Benefit Name',
            'status': 'Status',
        }