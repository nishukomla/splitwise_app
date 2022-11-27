from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import *


class NewUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user

class FriendForm(forms.Form):
	friendname = forms.CharField(max_length=100,required=True)

class GroupForm(forms.Form):
    # group_name = forms.CharField(label='Group name', max_length=100)
    group_name = forms.CharField()
    # friends = forms.MultipleChoiceField()

    # def current_frnd(self):
    #     friends = forms.MultipleChoiceField(choices=self.cleaned_data["username"])
    #     return friends


    # RANGE_SHORT = 's'
    # RANGE_MID = 'm'
    # RANGE_LONG = 'l'
    # RANGE_CHOICES = (
    #     (RANGE_SHORT, 'Sho'),
    #     (RANGE_MID, 'Mid range'),
    #     (RANGE_LONG, 'Long range')
    # )
    # friends = forms.MultipleChoiceField(choices=[])

    # def __init__(self, user, *args, **kwargs):
    #     super(GroupForm, self).__init__(*args, **kwargs)
    #     self.fields['friends'] = forms.MultipleChoiceField(
    #         choices=user
    #     )
