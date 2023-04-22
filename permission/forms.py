from django import forms

from django.contrib.auth.models import User, Permission
from django.forms.fields import MultipleChoiceField
from django.forms import models
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re


class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(
            queryset=User.objects.filter(is_superuser=False),
            widget=forms.Select(
                attrs = {
                    'class': 'form-control',
                    'id':'user',
                }),
            error_messages={
                'required':'User Cannot be Empty',
            })
    
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
        # print(cleaned_data.get('user'))
        # print(cleaned_data.get('permissions'))
        print(cleaned_data)
        

        return cleaned_data
    
    def clean_user(self):
        print('Enter Clean User')
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        errors = []
        print(user)

        if user is None:
            errors.append('Name Cannot be Empty')

        if errors:
            raise forms.ValidationError(errors)

        return user
    
    def clean_permissions(self):
        print('Enter Clean Permissions')
        cleaned_data = super().clean()
        permissions = cleaned_data.get('permissions')
        errors = []
        print(permissions)

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