from django import forms

from .models import Leaves, LeaveBalances
from employees.models import Employees


class LeavesForm(forms.ModelForm):
    class Meta:
        model = Leaves
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'name': {
                'required': 'Leave Name is Required'
            },
            'max_duration': {
                'required': 'Duration Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Leave Name',
                'required': True,
                'id':'name',
                
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':'Enter Leave Description',
                'required': True,
                'id':'description',
                
            }),
            'max_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Max Duration',
                'required': True,
                'id':'max_duration',
                
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'name': 'Leave Name',
            'description': 'Leave Description',
            'duration': 'Leave Duration',
            'status': 'Status',
        }

class LeaveBalancesForm(forms.ModelForm):
    employee_id = forms.ModelChoiceField(
                    queryset = Employees.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'employee_id',
                        }),
                    required=True,
                    label='Employees',
                    to_field_name='hash_uuid')
    
    leave_id = forms.ModelChoiceField(
                    queryset = Leaves.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'leave_id',
                        }),
                    required=False,
                    label='Leaves Type',
                    to_field_name='hash_uuid')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].initial = kwargs.pop('initial_employee_id', None)
        
    class Meta:
        model = LeaveBalances
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'status']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {}

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Balance',
                'required': True,
                'id':'balance',
                
            }),
            'expired_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
                'id':'expired_at',
                
            }),
        }
        labels = {
            'balance': 'Leave Balance',
        }