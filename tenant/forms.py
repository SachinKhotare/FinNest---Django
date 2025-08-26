from django import forms
from .models import RaiseIssue, VacateNotice

class TenantLoginForm(forms.Form):
    id = forms.IntegerField(label="Tenant ID")  # match HTML input name
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

class RaiseIssueForm(forms.ModelForm):
    class Meta:
        model = RaiseIssue
        fields = [
            'title',
            'category',
            'urgency',
            'estimated_resolution_date',
            'details',
            'image'
        ]
        widgets = {
            'estimated_resolution_date': forms.DateInput(attrs={
                'type': 'date',
                'readonly': 'readonly'
            }),
            'details': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the issue in detail'
            }),
        }


# vacate

class VacateNoticeForm(forms.ModelForm):
    class Meta:
        model = VacateNotice
        fields = ['name', 'flat_no', 'reason']
