from django import forms
from django.contrib.auth.models import User
from cmumc.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

UserType = (
    ('H', 'Helper'),
    ('R', 'Receiver'),
)

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    user_name = forms.CharField(max_length=40)
    email = forms.EmailField(max_length=40, label="Email", widget=forms.EmailInput())
    password1 = forms.CharField(max_length=40, label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=40, label="Comfirm Password", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if User.objects.filter(username__exact=user_name):
            raise forms.ValidationError("User name has already taken")
        return user_name

    ##show detailed messages when register errors
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except:
            raise forms.ValidationError("Email format is not valid")

        if not email.endswith("cmu.edu"):
            raise forms.ValidationError("Email is not cmu email")
        return email

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        return cleaned_data

class ModeForm(forms.Form):
    mode = forms.CharField(max_length=1)

    def clean(self):
        cleaned_data = super(ModeForm, self).clean()
        return cleaned_data

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'category', 'date', 'time', 'location', 'price')
        widgets = {'date': forms.DateInput(format="%m/%d/%Y")}

    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price should be greater than 0")
        return price

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'activation_key', 'user_type')

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data

class MessageForm(forms.Form):
    body = forms.TextField(max_length=500, blank=False)

    def clean(self):
        cleaned_data = super(MessageForm, self).clean()
        return cleaned_data



