from django import forms

from employees.models import Employees
from .models import Presences

class PresenceBulkInputForm(forms.Form):
    file_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'id':'file_upload',
            'class': 'form-control',
            'accept': '.xls, .xlsx',
        }),
        label= 'Upload File Presence',
    )

class PresencesForm(forms.ModelForm):
    employee_id = forms.ModelChoiceField(
                    queryset = Employees.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'employee_id',
                        }),
                    required=True,
                    label='Employees',
                    to_field_name='hash_uuid')
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].initial = kwargs.pop('initial_employee_id', None)

    class Meta:
        model = Presences
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'start_at': {
                'required': 'Start At is Required'
            },
            'end_at': {
                'required': 'End At is Required'
            },
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'employee_id': forms.Select(attrs={
                'required': True,
                'id':'employee_id',
                
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
            'start_at': 'Start At',
            'end_at': 'End At',
            'status': 'Status',
            'employee_id': 'Employee',
        }