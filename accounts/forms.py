from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Transaction, Account, Category
from PIL import Image
from django.core.exceptions import ValidationError
from datetime import datetime

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
        fields = ['name', 'type', 'icon', 'color', 'budget_limit']
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
            'budget_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Budget limit (optional)',
                'step': '0.01',
                'min': '0'
            }),
        }

class ProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'profile_picture',
            'date_of_birth', 'country_code', 'phone_number',
            'occupation', 'bio', 'preferred_currency'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'readonly': 'readonly'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/png,image/jpeg',
                'id': 'profilePictureInput'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'country_code': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (without country code)',
                'pattern': '[0-9]{7,15}'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your occupation or job title'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Short bio about yourself (max 500 characters)',
                'rows': 4,
                'maxlength': '500'
            }),
            'preferred_currency': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_date_of_birth(self):
        """Validate date of birth"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.now().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 13:
                raise ValidationError('You must be at least 13 years old.')
            if age > 150:
                raise ValidationError('Please enter a valid date of birth.')
        return dob

    def clean_profile_picture(self):
        """Validate profile picture"""
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Check file size (max 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError('Profile picture must be less than 5MB.')
            
            # Check file type
            if hasattr(picture, 'content_type') and picture.content_type:
                if not picture.content_type.startswith('image'):
                    raise ValidationError('Please upload a valid image file.')
            
            # Check file extension
            filename = picture.name.lower()
            if not (filename.endswith(('.png', '.jpg', '.jpeg'))):
                raise ValidationError('Please upload a PNG or JPG image file.')
            
            # Try to open and validate the image
            try:
                img = Image.open(picture)
                img.verify()
            except Exception as e:
                raise ValidationError('Invalid image file. Please upload a valid PNG or JPG.')
        
        return picture

    def clean_phone_number(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.replace(' ', '').replace('-', '').isdigit():
            raise ValidationError('Phone number must contain only digits, spaces, or hyphens.')
        return phone