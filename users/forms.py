from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .utils import valida_rut_chile

from .models import UserAccount


class UserAddForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserAccount
        fields = ['rut']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 is not None and password1 != password2:
            self.add_error("password2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = UserAccount
        fields = ['rut', 'email', 'password', 'is_active']

    def clean_password(self):
        return self.initial["password"]


class LoginForm(forms.Form):
    rut = forms.CharField(
        max_length=11, required=True, widget=forms.TextInput(attrs={'placeholder': 'Rut usuario'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Clave'}), required=True)

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not valida_rut_chile(rut):
            raise forms.ValidationError('Rut inválido.')
        return rut

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get('rut')
        password = cleaned_data.get('password')

        if not rut or not password:
            raise forms.ValidationError('Ambos campos son obligatorios.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Ingresar'))
