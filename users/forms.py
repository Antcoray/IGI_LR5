import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from catalog.models import Client, Employee



def validate_phone(value):
    pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Телефон в формате +375 (XX) XXX-XX-XX')
    

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50, label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['phone', 'address', 'birth_date', 'city', 'email']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+375 (29) XXX-XX-XX'
            }),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        validate_phone(phone)
        return phone

    def clean_birth_date(self):
        from django.utils import timezone
        bd = self.cleaned_data.get('birth_date')
        if bd:
            today = timezone.now().date()
            age = (today - bd).days // 365
            if age < 18:
                raise ValidationError('Возраст должен быть 18+')
        return bd
