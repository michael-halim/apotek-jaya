from django import forms

from django.contrib.auth.models import User, Permission, Group

from employees.models import Employees

class PermissionForm(forms.Form):
    employees = forms.ModelChoiceField(
        queryset = Employees.objects.all(),
        widget = forms.Select(
                    attrs = {
                        'id':'employees',
                    }),
        error_messages={
            'required':'Employees Cannot be Empty',
        }
    )
    
    permissions = forms.ModelMultipleChoiceField(
        queryset = Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple(
                    attrs = {
                        'class':'form-check-input',
                    }),
        label = 'Permissions',
        error_messages={
            'required':'Permission Cannot be Empty',
        }
    )
    
    def clean(self):
        print('Enter Clean All')
        cleaned_data = super().clean()
        print(cleaned_data)

        return cleaned_data
    
    def clean_employees(self):
        print('Enter Clean Employees')
        cleaned_data = super().clean()
        employees = cleaned_data.get('employees')
        errors = []

        if employees is None:
            errors.append('Name Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return employees
    
    def clean_permissions(self):
        print('Enter Clean Permissions')
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        errors = []

        if permissions is None:
            errors.append('Permission Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return permissions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        permissions_choices = []
        for perm in Permission.objects.all():
            permissions_choices.append(
                (perm.id, perm.name.replace('Can','').strip().title())
            )
        
        self.fields['permissions'].choices = permissions_choices
        
        employees = []
        for emp in Employees.objects.all():
            if len(emp.auth_user_id.user_permissions.all()) == 0:
                employees.append(emp.id)
        
        employees = Employees.objects.filter(id__in = employees)

        initial_data = kwargs.pop('initial', [])

        if initial_data:
            employees = Employees.objects.filter(id__in = initial_data['employees'])

        self.fields['employees'].queryset = employees

class PermissionGroupForm(forms.Form):
    group = forms.CharField(
                label='Group Name',
                error_messages={
                    'required': 'Group Name Cannot be Empty',
                }, 
                widget=forms.TextInput(attrs={
                    'autofocus': False, 
                    'placeholder':'Enter Group Name',
                    'class': 'form-control',
                    'required': True,
                    'id':'group',
                })
            )  
    
    permissions = forms.ModelMultipleChoiceField(
                    queryset = Permission.objects.all(),
                    widget = forms.CheckboxSelectMultiple(
                                attrs = {
                                    'class':'form-check-input',
                                }),
                    label = 'Permissions',
                    error_messages={
                        'required':'Permission Cannot be Empty',
                    }
                )
    
    def clean(self):
        print('Enter Clean All')
        cleaned_data = super().clean()
        print(cleaned_data)

        return cleaned_data
    
    def clean_group(self):
        print('Enter Clean Group')
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        errors = []

        if group is None:
            errors.append('Group Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return group
    
    def clean_permissions(self):
        print('Enter Clean Permissions')
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        errors = []

        if permissions is None:
            errors.append('Permission Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return permissions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        permissions_choices = []
        for perm in Permission.objects.all():
            permissions_choices.append(
                (perm.id, perm.name.replace('Can','').strip().title())
            )
        
        self.fields['permissions'].choices = permissions_choices
        
        # employees = []
        # for emp in Employees.objects.all():
        #     if len(emp.auth_user_id.user_permissions.all()) == 0:
        #         employees.append(emp.id)
        
        # employees = Employees.objects.filter(id__in = employees)

        # initial_data = kwargs.pop('initial', [])

        # if initial_data:
        #     employees = Employees.objects.filter(id__in = initial_data['employees'])

        # self.fields['employees'].queryset = employees