from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class UserEditForm(forms.ModelForm):
    """Form for editing user details (without password)"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

class UserPasswordChangeForm(SetPasswordForm):
    """Form for changing user password by admin"""
    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')