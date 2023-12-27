from benefits.models import PTKPType
from django import forms

from .models import Employees

class EmployeesBulkInputForm(forms.Form):
    file_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'id':'file_upload',
            'class': 'form-control',
            'accept': '.xls, .xlsx',
        }),
        label= 'Upload File Employees',
    )

class EmployeesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ptkp_type_id'].initial = kwargs.pop('initial_ptkp_type_id', None)

    ptkp_type_id = forms.ModelChoiceField(
                    queryset = PTKPType.objects.all(),
                    widget=forms.Select(
                        attrs = {
                            'id':'ptkp_type_id',
                            'class':'form-control',
                        }),
                    required=False,
                    label='PTKP Type',
                    to_field_name='hash_uuid')
    
    def clean_name(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        errors = []

        if name is None:
            errors.append('Name Cannot be Empty')

        elif len(name) > 200:
            errors.append('Name Cannot be Longer Than 200 Letters')

        if errors:
            raise forms.ValidationError(errors)

        return name

    def clean_nik(self):
        cleaned_data = super().clean()
        nik = cleaned_data.get('nik')
        errors = []

        if nik is None:
            nik = ''
        
        elif len(nik) > 20:
            errors.append("NIK Cannot be Longer Than 20")
        
        if errors:
            raise forms.ValidationError(errors)
        
        return nik
    
    def clean_birthplace(self):
        cleaned_data = super().clean()
        birthplace = cleaned_data.get('birthplace')
        errors = []

        if birthplace is None :
            errors.append("Birthplace Cannot be Empty")
        
        if errors:
            raise forms.ValidationError(errors)
        
        return birthplace
    

    def clean_birthdate(self):
        cleaned_data = super().clean()
        birthdate = cleaned_data.get('birthdate')

        return birthdate
    
    def clean_bloodtype(self):
        cleaned_data = super().clean()
        bloodtype = cleaned_data.get('bloodtype')
        
        return bloodtype

    def clean_address(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        
        return address

    def clean_rt(self):
        cleaned_data = super().clean()
        rt = cleaned_data.get('rt')
        
        return rt
    
    def clean_rw(self):
        cleaned_data = super().clean()
        rw = cleaned_data.get('rw')

        return rw
    
    def clean_province(self):
        cleaned_data = super().clean()
        province = cleaned_data.get('province')

        return province
    
    def clean_domicile(self):
        cleaned_data = super().clean()
        domicile = cleaned_data.get('domicile')

        return domicile
    
    def clean_gender(self):
        cleaned_data = super().clean()
        gender = cleaned_data.get('gender')

        return gender

    def clean_phone(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')

        return phone
    
    def clean_npwp(self):
        cleaned_data = super().clean()
        npwp = cleaned_data.get('npwp')

        return npwp
    
    def clean_expired_at(self):
        cleaned_data = super().clean()
        expired_at = cleaned_data.get('expired_at')

        return expired_at
    
    def clean_education(self):
        cleaned_data = super().clean()
        education = cleaned_data.get('education')

        return education
    
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
        model = Employees
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'resigned_at', 'join_date', 'auth_user_id', 
                   'birthplace', 'bloodtype', 'address', 'rt', 'rw', 'province', 'domicile', 
                   'phone', 'education', 'ptkp_type_id']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'nik': {
                'required': 'NIK is Required'
            },
            'name': {
                'required': 'Name is Required'
            },
            'birthdate': {
                'required': 'Birthdate is Required'
            }
        }

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Name',
                'required': True,
                'id':'name',
                
            }),
            'nik': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'0xxx 16 Digit',
                'required': False,
                'id':'nik',
                
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'required': False,
                'id':'birthdate',
                'type':'date',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': False,
                'id':'gender',
                
            }),
            'npwp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'0xxx',
                'required': False,
                'id':'npwp',
            }),
            'expired_at': forms.DateInput(attrs={
                'class': 'form-control',
                'required': False,
                'id':'expired_at',
                'type':'date'
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': False,
                'id':'status',
            }),
        }
        labels = {
            'nik':'NIK',
            'birthdate': 'Birthdate',
            'npwp': 'NPWP',
            'expired_at':'Expired At',
            'status': 'Status',
        }