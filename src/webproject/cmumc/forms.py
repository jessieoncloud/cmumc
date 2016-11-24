from django import forms
from django.contrib.auth.models import User
from cmumc.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import datetime

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
            raise forms.ValidationError("User name is already taken")
        return user_name

    ##show detailed messages when register errors
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except:
            raise forms.ValidationError("Email format is not valid")

        if not email.endswith("cmu.edu"):
            raise forms.ValidationError("Please enter a valid CMU email address")
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
        fields = ('title', 'description', 'category', 'date', 'time', 'price', 'post_photo')
        widgets = {'date': forms.DateInput(format="%m/%d/%Y", attrs={'class': 'datepicker'}),
                   'time': forms.TimeInput(format='%I:%M %p', attrs={'data-toggle': 'tooltip', 'title': 'Format: "18:00"'}),
                   'post_photo': forms.FileInput()}

    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price should be greater than 0")
        return price

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < datetime.datetime.today():
            raise forms.ValidationError("Date should be later than today")
        return date

    def clean_time(self):
        time = self.cleaned_data.get('time')
        if date == datetime.datetime.today() and time < datetime.datetime.now():
            raise forms.ValidationError("Time should be greater than current time")
        return time

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'activation_key', 'user_type', 'helper_punctuality_score', 'helper_quality_score',
                   'receiver_punctuality_score', 'receiver_quality_score')
        widgets = {'phone': forms.TextInput(
            attrs={'data-toggle': 'tooltip', 'title': 'Format: +14121111111'}), 'photo': forms.FileInput()}

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data

class MessageForm(forms.Form):
    body = forms.CharField(max_length=500, widget=forms.Textarea())

    def clean(self):
        cleaned_data = super(MessageForm, self).clean()
        return cleaned_data

class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=40)

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()
        return cleaned_data

class RateForm(forms.ModelForm):
    class Meta:
        model = Rating
        exclude = ('created_user', 'task')

    def clean(self):
        cleaned_data = super(RateForm, self).clean()
        return cleaned_data

    def clean_score(self):
        score = self.cleaned_data['score']
        if score < 0.0 or score > 5.0:
            raise forms.ValidationError("Rating score is out of range")
        return score


