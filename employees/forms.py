from django import forms

from .models import Employees
from .constants import PROVINCE

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

class EmployeesForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        print('Enter Clean')
        print(cleaned_data)

        return cleaned_data
    
    def clean_name(self):
        print('Enter Clean Name')
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
        print('Enter Clean NIK')
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
        print('Enter Clean Birthplace')
        cleaned_data = super().clean()
        birthplace = cleaned_data.get('birthplace')
        errors = []

        if birthplace is None :
            errors.append("Birthplace Cannot be Empty")
        
        if errors:
            raise forms.ValidationError(errors)
        
        return birthplace
    

    def clean_birthdate(self):
        print('Enter Clean Birthdate')
        cleaned_data = super().clean()
        birthdate = cleaned_data.get('birthdate')
        errors = []

        if birthdate is None :
            errors.append("Birthdate Cannot be Empty")

        else:
            diff = datetime.now(ZoneInfo('Asia/Bangkok')).date() - birthdate
            years_old = diff.days / 365
            if diff.days == 0:
                errors.append('Birthdate Cannot be Today')

            elif years_old < 17:
                errors.append('Minimum Age of Employee is 17')

        if errors:
            raise forms.ValidationError(errors)
        
        return birthdate
    
    def clean_bloodtype(self):
        print('Enter Clean Bloodtype')
        cleaned_data = super().clean()
        bloodtype = cleaned_data.get('bloodtype')
        errors = []

        if bloodtype is None :
            bloodtype = ''

        else:
            bloodtype = bloodtype.replace(' ','').lower()
            bloodtype_choices = ['a+', 'a-', 'b+', 'b-', 'o+', 'o-', 'ab+', 'ab-', 'a', 'b','o', 'ab']

            if bloodtype not in bloodtype_choices:
                errors.append('Please enter a valid bloodtype')

        if errors:
            raise forms.ValidationError(errors)
        
        return bloodtype

    def clean_address(self):
        print('Enter Clean Address')
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        errors = []

        if address is None :
            address = ''

        else:
            # Remove white spaces at the beginning and end of the string
            address = address.strip()
            address = re.sub(r'[^\w\s,.]', '', address)

            if len(address) > 400:
                errors.append('Address Cannot Be Longer Than 400 Characters')

            else:
                # Capitalize the first letter of each word in the address
                address = ' '.join(word.capitalize() for word in address.split())
                
                # Replace any double white spaces with a single space
                address = ' '.join(address.split())

        if errors:
            raise forms.ValidationError(errors)
        
        return address

    def clean_rt(self):
        print('Enter Clean RT')
        cleaned_data = super().clean()
        rt = cleaned_data.get('rt')
        errors = []

        if rt is None:
            errors.append('RT Cannot be Empty')

        else:
            rt = rt.strip()
            if not rt.isnumeric():
                errors.append('RT Must Only Contain Number 0-9')

        if errors:
            print('ENTER ERRORS RT')
            raise forms.ValidationError(errors)
        
        return rt
    
    def clean_rw(self):
        print('Enter Clean RW')
        cleaned_data = super().clean()
        rw = cleaned_data.get('rw')
        errors = []
        if rw is None:
            errors.append('RW Cannot be Empty')
        
        else:
            rw = rw.strip()
            if not rw.isnumeric():
                errors.append('RW Must Only Contain Number 0-9')

        if errors:
            raise forms.ValidationError(errors)

        return rw
    
    def clean_province(self):
        print('Enter Clean Province')
        cleaned_data = super().clean()
        province = cleaned_data.get('province')
        errors = []
        if province is None:
            errors.append('Province Cannot be Empty')

        elif province != '':
            province_choices = [x[1] for x in PROVINCE]
            if province not in province_choices:
                errors.append('Province is Not Valid')

        if errors:
            raise forms.ValidationError(errors)

        return province
    
    def clean_domicile(self):
        print('Enter Clean Domicile')
        cleaned_data = super().clean()
        domicile = cleaned_data.get('domicile')
        errors = []
        if domicile is None:
            domicile = ''

        else:
            # Remove white spaces at the beginning and end of the string
            domicile = domicile.strip()
            domicile = re.sub(r'[^\w\s,.]', '', domicile)

            if len(domicile) > 400:
                errors.append('Domicile Cannot Be Longer Than 400 Characters')

            else:
                # Capitalize the first letter of each word in the domicile
                domicile = ' '.join(word.capitalize() for word in domicile.split())
                
                # Replace any double white spaces with a single space
                domicile = ' '.join(domicile.split())

        if errors:
            raise forms.ValidationError(errors)

        return domicile
    
    def clean_gender(self):
        print('Enter Clean Gender')
        cleaned_data = super().clean()
        gender = cleaned_data.get('gender')
        errors = []

        if gender is None:
            errors.append('gender Cannot be Empty')

        elif gender != '':
            gender = gender.strip().upper()
            
            gender_choices = ['L', 'P']

            if gender not in gender_choices:
                print('gender not valid')
                errors.append('gender is not valid')

        if errors:
            raise forms.ValidationError(errors)

        print('returning gender')
        return gender

    def clean_phone(self):
        print('Enter Clean Phone')
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        errors = []
        if phone is None:
            phone = ''

        else:
            phone = phone.strip()
            if not phone.isnumeric():
                errors.append('Phone Number Must Only Contain Number 0-9')

            elif len(phone) > 15:
                errors.append('Phone Number Cannot be Longer Than 15 Numbers')

        if errors:
            raise forms.ValidationError(errors)

        return phone
    
    def clean_npwp(self):
        print('Enter Clean NPWP')
        cleaned_data = super().clean()
        npwp = cleaned_data.get('npwp')
        errors = []
        if npwp is None:
            npwp = ''

        else:
            npwp = npwp.strip()
            if not npwp.isnumeric():
                errors.append('NPWP Number Must Only Contain Number 0-9')

            elif len(npwp) > 16:
                errors.append('NPWP Number Cannot be Longer Than 16 Numbers')

        if errors:
            raise forms.ValidationError(errors)

        return npwp
    
    def clean_expired_at(self):
        print('Enter Clean Expired At')
        cleaned_data = super().clean()
        expired_at = cleaned_data.get('expired_at')
        errors = []

        if expired_at is None:
            expired_at = datetime.now(ZoneInfo('Asia/Bangkok')).date() + timedelta(days=365)

        else:
            diff = datetime.now(ZoneInfo('Asia/Bangkok')).date() - expired_at
            if diff.days > 0:
                errors.append('Please select a date in the future for this field')

        if errors:
            raise forms.ValidationError(errors)

        return expired_at
    
    def clean_education(self):
        print('Enter Clean Education')
        cleaned_data = super().clean()
        education = cleaned_data.get('education')
        errors = []
        if education is None:
            education = ''

        else:
            education = education.strip()
            if not education.isalnum():
                errors.append('Education Must be Alphanumeric')

            elif len(education) > 10:
                errors.append('Education Cannot be More Than 10 Characters')
        if errors:
            raise forms.ValidationError(errors)

        return education
    
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
        model = Employees
        exclude = ['updated_at', 'updated_by', 'created_by', 'created_at', 
                   'deleted_at', 'deleted_by', 'resigned_at', 'join_date', 'auth_user_id']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {
            'nik': {
                'required': 'This is My bUiltd in'
            },
            'name': {
                'required': 'Name is Required'
            },
            'birthplace': {
                'required': 'Birthplace is Required'
            },
            'birthdate': {
                'required': 'Birthdate is Required'
            },
            'province': {
                'required': 'Province is Required'
            },
            'rt': {
                'required': 'RT is Required'
            },
            'rw': {
                'required': 'RW is Required'
            },
            'gender': {
                'required': 'Gender is Required'
            },
            'expired_at':{
                'required':'Expired At is Required'
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
            'birthplace': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Malang',
                'required': True,
                'id':'birthplace',
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'required': False,
                'id':'birthdate',
                'type':'date',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'id':'gender',
                
            }),
            'bloodtype': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'A+ / A- / B+ / B- / O+ / O- / AB+ / AB-',
                'required': False,
                'id':'bloodtype',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':'Jl. Kebayoran....',
                'required': False,
                'id':'address',
            }),
            'rt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'10',
                'required': False,
                'id':'rt',
            }),
            'rw': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'10',
                'required': False,
                'id':'rw',
            }),
            'province': forms.Select(attrs={
                'class': 'form-control',
                'required': False,
                'id':'province',
            }),
            'domicile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'Domicile',
                'required': False,
                'id':'domicile',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'081xxxxxxxxx',
                'required': False,
                'id':'phone',
            }),
            'npwp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'0xxx',
                'required': False,
                'id':'npwp',
            }),
            'education': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':'SMA',
                'required': False,
                'id':'education',
            }),
            'expired_at': forms.DateInput(attrs={
                'class': 'form-control',
                'required': True,
                'id':'expired_at',
                'type':'date'
            }),
            'status': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':'1',
                'required': True,
                'id':'status',
            }),
        }
        labels = {
            'nik':'NIK',
            'birthplace': 'Birthplace',
            'birthdate': 'Birthdate',
            'bloodtype': 'Blood Type',
            'address': 'Address',
            'rt': 'RT',
            'rw': 'RW',
            'province': 'Province',
            'domicile': 'Domicile',
            'phone': 'Phone',
            'npwp': 'NPWP',
            'education': 'Education',
            'expired_at':'Expired At',
            'status': 'Status',
        }