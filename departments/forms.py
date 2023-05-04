from django import forms
from django.contrib.auth.models import Group
from employees.models import Employees
from .models import DepartmentMembers, Departments

class DepartmentMembersForm(forms.ModelForm):
    employee_id = forms.ModelMultipleChoiceField(
                    queryset = Employees.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'employees',
                        }
                    ),
                    required=False,
                    label='Employees',
                    to_field_name='hash_uuid')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_employee_id(self):
        return None
    
    class Meta:
        model = DepartmentMembers
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'department_id', 'status']
        
class DepartmentMembersPermissionGroupForm(forms.Form):
    group = forms.ModelChoiceField(
                    queryset = Group.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'group',
                        }),
                    required=False,
                    label='Permission Group',
                )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_group(self):
        return None
    
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