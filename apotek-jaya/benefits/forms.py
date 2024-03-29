from django import forms
from django.contrib.auth.models import Group

from departments.models import Departments

from .models import BenefitCategories, BenefitScheme, Benefits, DetailEmployeeBenefits, PTKPType

class PtkpTypeBulkInputForm(forms.Form):
    file_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'id':'file_upload',
            'class': 'form-control',
            'accept': '.xls, .xlsx',
        }),
        label= 'Upload File Ptkp Type',
    )

class BenefitsForm(forms.ModelForm):
    benefit_category_id = forms.ModelChoiceField(
                    queryset = BenefitCategories.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'benefit_category',
                            'class':'form-control',
                        }),
                    required=True,
                    label='Benefit Category',
                    to_field_name='hash_uuid')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['benefit_category_id'].initial = kwargs.pop('initial_benefit_category_id', None)

    def clean_name(self):
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
        cleaned_data = super().clean()
        value = cleaned_data.get('value')

        errors = []

        if value is None:
            errors.append('Value Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return value

    def clean_status(self):
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

class BenefitCategoriesForm(forms.ModelForm):
    def clean_name(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        errors = []

        if name is None:
            errors.append('Benefit Categories Name Cannot be Empty')

        elif len(name) <= 0:
            errors.append('Benefit Categories Name Cannot be Empty')

        elif len(name) > 200:
            errors.append('Benefit Categories Name Cannot be Longer Than 200 Letters')

        if errors:
            raise forms.ValidationError(errors)

        return name
    
    class Meta:
        model = BenefitCategories
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Benefit Categories Name is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Scheme Name',
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
            'name': 'Benefit Categories Name',
            'status': 'Status',
        }

class BenefitSchemeForm(forms.ModelForm):
    def clean_name(self):
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
    
    def clean_updated_value(self):
        cleaned_data = super().clean()
        updated_value = cleaned_data.get('updated_value')

        errors = []

        if updated_value is None:
            errors.append('Value Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return updated_value

    def clean_status(self):
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
        model = BenefitScheme
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Benefit Name is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Scheme Name',
                'required': True,
                'id':'name',
                
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Scheme Description Name',
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
            'name': 'Benefit Scheme Name',
            'status': 'Status',
        }

class DetailEmployeeBenefitsForm(forms.ModelForm):
    benefit_id = forms.ModelChoiceField(
                    queryset = Benefits.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'benefit',
                        }
                    ),
                    required=False,
                    label='Benefit',
                    to_field_name='hash_uuid',
                )
    
    department = forms.ModelChoiceField(
                    queryset = Departments.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'department',
                        }
                    ),
                    required=False,
                    label='Department',
                    to_field_name='hash_uuid',
                )
    
    def clean_status(self):
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
        model = DetailEmployeeBenefits
        exclude = ['employee_id','benefit_scheme_id', 'updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'status']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
        
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'benefit_id': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id':'benefit',
                
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'benefit_id': 'Benefit',
            'department': 'Department',
        }

class PTKPTypeForm(forms.ModelForm):
    def clean_name(self):
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
    
    def clean_value(self):
        cleaned_data = super().clean()
        value = cleaned_data.get('value')

        errors = []

        if value is None:
            errors.append('Value Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return value

    def clean_status(self):
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
        model = PTKPType
        fields = '__all__'

        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'PTKP Type is Required'
            },
            'value': {
                'required': 'PTKP Value is Required'
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
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Benefit Value',
                'required': True,
                'id':'value',
                
            }),
        }
        
        labels = {
            'name': 'PTKP Type Name',
            'value': 'PTKP Value',
        }
