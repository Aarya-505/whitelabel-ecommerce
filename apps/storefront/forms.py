from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class CustomerRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'First and last name',
            'autofocus': True,
            'id': 'reg_full_name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'name@domain.com',
            'id': 'reg_email'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'Choose username (optional, defaults to email)',
            'id': 'reg_username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'At least 6 characters',
            'id': 'reg_password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'Re-enter password',
            'id': 'reg_confirm_password'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists. Please sign in.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self):
        full_name = self.cleaned_data['full_name'].strip()
        email = self.cleaned_data['email'].strip().lower()
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        elif User.objects.filter(username=username).exists():
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        first_name = full_name
        last_name = ''
        if ' ' in full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=last_name
        )
        return user


class CustomerLoginForm(forms.Form):
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'Email or Username',
            'autofocus': True,
            'id': 'login_ident'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control luxury-input',
            'placeholder': 'Enter your password',
            'id': 'login_password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        ident = cleaned_data.get('username_or_email', '').strip()
        password = cleaned_data.get('password', '')

        if ident and password:
            user = None
            if '@' in ident:
                user_obj = User.objects.filter(email__iexact=ident).first()
                if user_obj:
                    user = authenticate(username=user_obj.username, password=password)
            if not user:
                user = authenticate(username=ident, password=password)

            if not user:
                raise ValidationError("Invalid email/username or password. Please check your credentials.")
            if not user.is_active:
                raise ValidationError("This account is currently disabled.")
            cleaned_data['user'] = user

        return cleaned_data
