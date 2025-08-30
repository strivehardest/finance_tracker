from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Transaction, Account, Category

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'date', 'category', 'account', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Optional notes'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'type', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account name'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'balance': forms.NumberInput(attrs={
                'step': '0.01', 
                'class': 'form-control',
                'placeholder': '0.00'
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '💰'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'form-control form-control-color'
            }),
        }