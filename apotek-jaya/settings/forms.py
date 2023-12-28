from django import forms

from .models import Settings

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ['hash_uuid']
        
        # Error Messages Here's Defined Because in models.py it is set to null=False implicitly
        error_messages = {}

        # If you specify 'id', tags 'id_for_label' is also set
        widgets= {
            'overtime_rate': forms.TextInput(attrs={
                'class': 'form-control',
                'required': False,
                'id':'overtime_rate',
                
            }),
            'lembur_rate': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'required': False,
                'id':'lembur_rate',
                
            }),
        }
        
        labels = {
            'overtime_rate': 'Overtime Rate',
            'lembur_rate': 'Lembur Rate',
        }