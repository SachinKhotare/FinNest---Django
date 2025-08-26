from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'date_of_birth', 'gender',
            'mobile_no', 'address', 'profile_pic', 'account_type',
            'password1', 'password2'
        ]

class UserLoginForm(forms.Form):
    id = forms.IntegerField(label="User ID")  # match HTML input name
    password = forms.CharField(widget=forms.PasswordInput, label="Password")