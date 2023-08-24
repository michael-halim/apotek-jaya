from django import forms
from django.contrib.auth.models import Group

from employees.models import Employees
from .models import PayrollPeriods, Salaries, SalaryAdjustments

class SalaryAdjustmentsForm(forms.ModelForm):
    class Meta:
        model = SalaryAdjustments
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'status']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'value':{
                'required': 'Salary Adjustment Value is Required'
            }
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Salary Adjustment Name',
                'required': False,
                'id':'name',
                
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Salary Adjustment Description',
                'required': False,
                'id':'description',
            }),
            'is_deduction': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': False,
                'id':'is_deduction',
            }),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Salary Adjustment Value',
                'required': True,
                'id':'value',
            })
        }

        labels = {
            'name': 'Salary Adjustment Name',
            'description': 'Salary Adjustment Description',
            'is_deduction': 'Is Deduction',
            'value': 'Salary Adjustment Value',
        }
    

class SalariesForm(forms.ModelForm):
    employee_id = forms.ModelChoiceField(
                    queryset = Employees.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'employee_id',
                            'class':'form-control',
                        }),
                    required=True,
                    label='Employee',
                    to_field_name='hash_uuid')
    
    period_id = forms.ModelChoiceField(
                    queryset = PayrollPeriods.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'period_id',
                            'class':'form-control',
                        }),
                    required=True,
                    label='Period',
                    to_field_name='hash_uuid')
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].initial = kwargs.pop('initial_employee_id', None)
        self.fields['period_id'].initial = kwargs.pop('initial_period_id', None)

    class Meta:
        model = Salaries
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'presence_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Presence Count',
                'required': False,
                'id':'presence_count',
            }),
            'total_work_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Total Work Hours',
                'required': False,
                'id':'total_work_hours',
            }),
            'ptkp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Payroll Period Description',
                'required': False,
                'id':'ptkp',
                
            }),
            'overtime_hours_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Overtime Hours',
                'required': False,
                'id':'overtime_hours_count',
                
            }),
            'overtime_hours_nominal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Overtime Hours Nominal',
                'required': False,
                'id':'overtime_hours_nominal',
                
            }),
            'leave_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Leave Count',
                'required': False,
                'id':'leave_count',
                
            }),
            'sick_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Sick Count',
                'required': False,
                'id':'sick_count',
                
            }),
            'permit_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Permit Count',
                'required': False,
                'id':'permit_count',
                
            }),
            'pph21': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter PPh21',
                'required': False,
                'id':'pph21',
                
            }),
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Employee',
                'required': False,
                'id':'employee_id',
                
            }),
            'period_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Period',
                'required': False,
                'id':'period_id',
                
            }),
            'final_salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Final Salary',
                'required': False,
                'id':'final_salary',
                
            }),
            'gross_salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Gross Salary',
                'required': False,
                'id':'gross_salary',
                
            }),
            'allowance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Allowance',
                'required': False,
                'id':'allowance',
                
            }),
            'base_salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Base Salary',
                'required': False,
                'id':'base_salary',
                
            }),
            'bonus': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Bonus',
                'required': False,
                'id':'bonus',
                
            }),
            'deduction': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Sick Count',
                'required': False,
                'id':'deduction',
                
            }),
            'thr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter THR Value',
                'required': False,
                'id':'thr',
                
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
            'thr': 'THR',
            'status': 'Status',
        }

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