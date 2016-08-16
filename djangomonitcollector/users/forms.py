# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

from allauth.account.forms import SignupForm
from django.utils.translation import ugettext as _

from .models import User, Organisation, INSPINIA_SKINS
from djangomonitcollector.datacollector.lib.utils import TIMEZONES_CHOICES


class MyUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class MySignUpForm(SignupForm):
    pass


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    first_name = forms.CharField(label=_("Firstname"), required=False)
    last_name = forms.CharField(label=_("Lastname"),  required=False)
    email = forms.CharField(
        label=_("Email"), widget=forms.EmailInput, required=False)
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        required=False
    )

    organisation_manager = forms.BooleanField(required=False)

    inspinia_skin = forms.ChoiceField(
        label=_("Inspinia Skin"),
        widget=forms.Select,
        choices=INSPINIA_SKINS,
        required=False
    )

    user_timezone = forms.ChoiceField(
        label=_("User Timezone"),
        widget=forms.Select,
        choices=TIMEZONES_CHOICES,
        required=False,
        initial="Canada/Eastern"
    )

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_organisation(self):
        organisation = self.cleaned_data["organisation"]
        return organisation

    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.instance.username = self.cleaned_data["username"]
        self.instance.set_password(password)
        self.instance.first_name = self.cleaned_data["first_name"]
        self.instance.last_name = self.cleaned_data["last_name"]
        self.instance.email = self.cleaned_data["email"]
        self.instance.user_timezone = self.cleaned_data["user_timezone"]
        self.instance.inspinia_skin = self.cleaned_data["inspinia_skin"]
        self.instance.organisation_manager = self.cleaned_data[
            "organisation_manager"]
        self.instance.organisation = self.cleaned_data['organisation']
        if commit:
            self.instance.save()
        return self.instance


class CustomPasswordChangeForm(AdminPasswordChangeForm):
    pass
