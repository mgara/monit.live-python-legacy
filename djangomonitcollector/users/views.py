# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import uuid
import logging

from braces.views import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView,\
    ListView,\
    RedirectView,\
    UpdateView,\
    CreateView,\
    DeleteView

from .models import User, CollectorKey, APIKey, UserSettings
from .forms import MyUserCreationForm, CustomPasswordChangeForm, OrganisationCreationForm


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserListView(LoginRequiredMixin, ListView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.model.objects.all()
        else:
            if user.organisation_manager:
                org = user.organisation
                # if the user is an organization manager, return all users that
                # are not superusers.
                return self.model.objects.filter(organisation=org, is_superuser=False)


class UserCreate(LoginRequiredMixin, CreateView):
    model = User
    form_class = MyUserCreationForm
    slug_field = "username"
    slug_url_kwarg = "username"

    # def form_invalid(self, form):
    #    response = super(UserCreate, self).form_invalid(form)
    #    print "DEBUG form_invalid"
    #    print self.__dict__
    #    return response

    def form_valid(self, form):
        organisation = form.cleaned_data['organisation']
        if not organisation:
            form.cleaned_data['organisation'] = self.request.user.organisation

        return super(UserCreate, self).form_valid(form)


class UserCreate(LoginRequiredMixin, CreateView):
    model = User
    form_class = MyUserCreationForm
    slug_field = "username"
    slug_url_kwarg = "username"

    # def form_invalid(self, form):
    #    response = super(UserCreate, self).form_invalid(form)
    #    print "DEBUG form_invalid"
    #    print self.__dict__
    #    return response

    def form_valid(self, form):
        organisation = form.cleaned_data['organisation']
        if not organisation:
            form.cleaned_data['organisation'] = self.request.user.organisation

        return super(UserCreate, self).form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User

    fields = [
        'first_name',
        'last_name',
        'email',
        'organisation_manager',
        'user_timezone',
        'host_groups'
    ]

    def dispatch(self, *args, **kwargs):
        if self.request.method == "GET":
            if self.request.user.is_superuser:
                self.fields.append('organisation')
                self.fields.remove('host_groups')
        return super(UserUpdateView, self).dispatch(*args, **kwargs)

    def form_invalid(self, form):

        response = super(UserUpdateView, self).form_invalid(form)
        return response

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if self.request.user.organisation_manager:
            if self.request.user.id == form.instance.id:
                form.instance.organisation_manager = True

        return super(UserUpdateView, self).form_valid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = '/users/'


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


@login_required
def UpdatePassword(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.user)
            return redirect('user:detail', username=form.user.username)

    return render(request, 'users/password.html', {
        'form': form,
    })


@login_required
def UpdatePasswordForUser(request, pk):
    current_user = User.objects.get(id=pk)
    form = CustomPasswordChangeForm(user=current_user)

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=current_user, data=request.POST)
        if form.is_valid():
            form.user.is_update = True
            form.user.hylafax_password = form.cleaned_data['password1']
            form.save()
            return redirect('users:detail', username=form.user.username)

    return render(request, 'users/password.html', {
        'form': form,
    })


def delete_collector_key(request):
    ck = request.POST['ck']
    Collector_key_instance = CollectorKey.objects.get(pk=ck)
    CollectorKey.delete(Collector_key_instance)

    res = {
        'status': "OK",
        'ck': ck
    }
    return JsonResponse(res)


def new_collector_key(request):
    org = request.user.organisation
    create = request.POST['create']
    if create in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        create = True
    else:
        create = False

    try:

        if create:
            #  org.collectorkey_set.all().delete()
            CollectorKey.create(uuid.uuid4(), org)
        html = ""
        organisation_keys = org.collectorkey_set.all()
        for ck in list(organisation_keys):
            html += build_collector_key_view(ck)

        res = {
            'data': html,
        }

    except StandardError as e:
        res = {
            'error': e.message,
            'error_id': 1
        }
    return JsonResponse(res)


def delete_api_key(request):
    apikey = request.POST['apikey']
    API_key_instance = APIKey.objects.get(pk=apikey)
    APIKey.delete(API_key_instance)

    res = {
        'status': "OK",
        'apikey': apikey
    }
    return JsonResponse(res)


def new_api_key(request):
    org = request.user.organisation
    create = request.POST['create']
    if create in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        create = True
    else:
        create = False

    try:

        if create:
            #  org.collectorkey_set.all().delete()
            APIKey.create(uuid.uuid4(), org)
        html = ""
        organisation_keys = org.apikey_set.all()
        for apikey in list(organisation_keys):
            html += build_api_key_view(apikey)

        res = {
            'data': html,
        }

    except StandardError as e:
        res = {
            'error': e.message,
            'error_id': 1
        }
    return JsonResponse(res)


def update_user_settings(request):
    key = request.POST['key']
    val = request.POST['val']

    user = request.user
    try:
        user_setting_instance = UserSettings.objects.get(user=user, key=key)
        UserSettings.delete(user_setting_instance)
    except UserSettings.DoesNotExist:
        pass

    try:
        UserSettings.create(user, key, val)

        res = {
            'status': "OK",
            'key': key,
            'val': val
        }
    except StandardError:
        res = {
            'status': "ERR",
            'key': "ERR",
            'val': "ERR"
        }

    return JsonResponse(res)


def build_api_key_view(apikey):
    res = ' <li class="p-10  ck-item" id="{0}">\
    <h2 style="font-family: \'Abel\', cursive;"><span class="btn btn-circle \
    btn-danger" data-toggle="tooltip" data-placement="left" title="" data-original-title="Delete" onclick="delete_api_key(this)" data-key="{0}" ><i class="\
    fa fa-trash"></i></span> {0}  \
    </h2></li>'.format(apikey.api_key)
    return res


def build_collector_key_view(ck):
    res = ' <li class="p-10  ck-item" id="{0}">\
    <h2 style="font-family: \'Abel\', cursive;"><span class="btn btn-circle \
    btn-danger" data-toggle="tooltip" data-placement="left" title="" data-original-title="Delete" onclick="delete_key(this)" data-key="{0}" ><i class="\
    fa fa-trash"></i></span><span class="btn btn-circle \
    btn-info" data-toggle="tooltip" data-placement="left" title="" data-original-title="Use" onclick="use(this)" data-key="{0}" ><i class="\
    fa fa-check" ></i></span> {0}  \
    </h2></li>'.format(ck.collector_key)
    return res
