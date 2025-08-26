from django import forms
from .models import Tenant, AddStock,AddSIP, Transaction

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'

#add stock

class AddStockForm(forms.ModelForm):
    class Meta:
        model = AddStock
        fields = ['stock_name', 'quantity', 'buy_price', 'current_price']

        widgets = {
            'stock_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stock name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'buy_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter buy price'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter current price'}),
        }

#add stock

class UpdateStockForm(forms.Form):
    stock = forms.ModelChoiceField(
        queryset=AddStock.objects.none(),  # will be set in view
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter additional quantity'})
    )
    new_buy_price = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter buy price for new units'})
    )

class AddSIPForm(forms.ModelForm):
    class Meta:
        model = AddSIP
        fields = ['sip_name', 'monthly_amount', 'due_date']

        widgets = {
            'sip_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SIP name'}),
            'monthly_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Monthly Amount'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter Due Date','type': 'date'}),
        }


class UpdateSIPForm(forms.Form):
    sip = forms.ModelChoiceField(
        queryset=AddSIP.objects.none(),  # set dynamically in view
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_monthly_amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter new monthly amount'})
    )
    new_due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
#expense

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'category', 'date', 'note']
