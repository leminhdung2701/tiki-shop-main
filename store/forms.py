from django.contrib.auth import password_validation
from store.models import Address
from django import forms
import django
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.db import models
from django.db.models import fields
from django.forms import widgets
from django.forms.fields import CharField
from django.utils.translation import gettext, gettext_lazy as _
from . models import Product, Comment


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Nhập mật khẩu'}))
    password2 = forms.CharField(label="Xác nhận mật khẩu", widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Nhập lại mật khẩu'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Nhập địa chỉ email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'username':'Tên tài khoản','email': 'Email'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Username'})}


class LoginForm(AuthenticationForm):
    username = UsernameField(label=_("Tên tài khoản"),widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label=_("Mậ khẩu"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'class':'form-control'}))


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['locality', 'city', 'state']
        widgets = {'locality':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ngõ 69B, đường 169 Nguyễn Trãi, Thanh Xuân'}), 'city':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Huyện/Thành Phố'}), 'state':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tỉnh'})}


class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Mật khẩu hiện tại"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'auto-focus':True, 'class':'form-control', 'placeholder':'Nhập mật khẩu hiện tại'}))
    new_password1 = forms.CharField(label=_("Mật khẩu mới"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Nhập mật khẩu mới'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Xác nhận mật khẩu mới"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Nhập lại mật khẩu mới'}))


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email', 'class':'form-control'}))


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Confirm Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password','class':'form-control'}))

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={'rows': '3',
                   'placeholder': 'Say Something...'}
        ))

    class Meta:
        model = Comment
        fields = ['comment']