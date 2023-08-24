from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django import forms

import re

class FileFieldForm(forms.Form):
    file_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )

class CreateUserForm(UserCreationForm):

    is_updating = False

    def __init__(self, *args, **kwargs):
        self.is_updating = kwargs.pop('is_updating', False)
        super().__init__(*args, **kwargs)

        if self.is_updating:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    password1 = forms.CharField(
                    label='Password',
                    error_messages={
                        'required': 'Password Cannot be Empty',
                        'min_length': 'Password Must be At Least 8 Characters Long',

                    }, 
                    widget=forms.PasswordInput(attrs={
                        'autofocus': False, 
                        'placeholder':'Enter Password',
                        'class': 'form-control',
                        'required': True,
                        'id':'password1',
                        'type':'password'
                    })
                )  
    
    password2 = forms.CharField(
                    label=  'Confirmation Password',
                    error_messages={
                        'required': 'Please Confirm Your Password',
                    },
                    widget=forms.PasswordInput(attrs={
                        'autofocus': False, 
                        'placeholder':'Enter Password Again',
                        'class': 'form-control',
                        'required': True,
                        'id':'password2',
                    })
                )  
    
    def clean_username(self):  
        print('Enter Clean Username')
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        errors = []

        if username is None:
            errors.append('Username Cannot be Empty')

        else:
            username = username.lower()
            found_username = User.objects.filter(username = username)  
            if found_username.count() and not self.is_updating:
                errors.append("User Already Exist")

            elif len(username.split()) > 1:
                errors.append('Username Must be 1 Word')

            elif len(username) > 150:
                errors.append('Username Cannot be More Than 150 Characters')


        if errors:
            raise forms.ValidationError(errors)

        return username  
  
    def clean_email(self):  
        print('Enter Clean Email')
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        errors = []
        
        if email is None:
            email = ''

        else:
            email = email.lower()
            email_found = User.objects.filter(email=email)  

            if email_found.count() and not self.is_updating:  
                errors.append('Email Already Exist')

            if not re.match(pattern=r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', string=email):
                errors.append('Email is Not Valid')

        if errors:
            raise forms.ValidationError(errors)
        
        return email  
  
    def clean_password2(self):  
        print('Enter Clean Password')
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
        errors = []

        if password1 and password2 and (password1 != password2):  
            errors.append('Password Does Not Match')

        if errors:
            raise forms.ValidationError(errors)
        return password2  

    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        
        widgets= {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'autofocus': False, 
                'placeholder':'Enter Unique Lowercase Characters',
                'required': True,
                'id':'username',
                
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder':'Enter Email',
                'autofocus': False, 
                'required': True,
                'id':'email',
                'type':'email'
                
            }),
        }
        error_messages = {
            'username': {
                'required': 'Username is Required'
            },
            'email': {
                'required': 'Email is Required'
            }
        }

        labels = {
            'username': 'Username',
            'email': 'Email',
        }
    