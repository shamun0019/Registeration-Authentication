from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email