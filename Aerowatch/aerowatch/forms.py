from django import forms
from django.contrib.auth.models import User

class Userform(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','password']
        widgets = {
            "email" : forms.EmailInput(attrs={'class': 'form-control'}),
            "password": forms.PasswordInput(attrs={'class': 'form-control'})
        }

class Registerform(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']
        widgets = {
            "first_name" : forms.TextInput(attrs={'class': 'form-control'}),
            "last_name" : forms.TextInput(attrs={'class': 'form-control'}),
            "email" : forms.EmailInput(attrs={'class': 'form-control'}),
            "password": forms.PasswordInput(attrs={'class': 'form-control'})
        }