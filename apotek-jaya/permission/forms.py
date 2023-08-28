from django import forms

from django.contrib.auth.models import User, Permission, Group

from employees.models import Employees

class PermissionForm(forms.Form):
    is_updating = False
    is_creating = False

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
        required=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
    
    def clean_employees(self):
        cleaned_data = super().clean()
        employees = cleaned_data.get('employees')
        errors = []

        if employees is None:
            errors.append('Name Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return employees
    
    def clean_permissions(self):
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        errors = []

        if errors:
            raise forms.ValidationError(errors)

        return permissions

    def __init__(self, *args, **kwargs):
        self.is_updating = kwargs.pop('is_updating', False)
        self.is_creating = kwargs.pop('is_creating', False)
        
        super().__init__(*args, **kwargs)

        permissions_choices = []
        for perm in Permission.objects.all():
            permissions_choices.append(
                (perm.id, perm.name.replace('Can','').strip().title())
            )
        
        self.fields['permissions'].choices = permissions_choices
        
        if self.is_creating:
            employees = []
            for emp in Employees.objects.all():
                if len(emp.auth_user_id.user_permissions.all()) == 0:
                    employees.append(emp.id)
            
            employees = Employees.objects.filter(id__in = employees)

            initial_data = kwargs.pop('initial', [])

            if initial_data:
                employees = Employees.objects.filter(id__in = initial_data['employees'])

            self.fields['employees'].queryset = employees

        if self.is_updating:
            self.fields['employees'].required = False

class PermissionGroupForm(forms.Form):
    is_updating = False

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
                    required=False,
                )
    
    status = forms.IntegerField(
                initial=1,
                required=True,
                label='Status',
                widget= forms.NumberInput(attrs={
                    'placeholder': 1,
                    'class':'form-control',
                    'id':'status',
                })
            )

    field_order = ['group', 'status', 'permissions']

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
    
    def clean_group(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        errors = []

        if group is None:
            errors.append('Group Cannot be Empty')

        else:
            found_group_name = Group.objects.filter(name = group)  
            if found_group_name.count() and not self.is_updating:
                errors.append("Group Permission Name Already Exist")

        if errors:
            raise forms.ValidationError(errors)

        return group
    
    def clean_status(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        errors = []

        if status is None:
            status = 1

        elif status < 0 or status > 3:
            errors.append('Status is Invalid')

        elif not isinstance(status, int):
            errors.append('Status Must Only Input Number')

        if errors:
            raise forms.ValidationError(errors)

        return status
    
    def clean_permissions(self):
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        errors = []

        if errors:
            raise forms.ValidationError(errors)

        return permissions

    def __init__(self, *args, **kwargs):
        self.is_updating = kwargs.pop('is_updating', False)
        super().__init__(*args, **kwargs)

        if self.is_updating:
            self.fields['group'].required = False

        permissions_choices = []
        for perm in Permission.objects.all():
            permissions_choices.append(
                (perm.id, perm.name.replace('Can','').strip().title())
            )
        
        self.fields['permissions'].choices = permissions_choices