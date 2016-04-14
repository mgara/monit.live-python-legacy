# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import uuid

from braces.views import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views.generic import DetailView,\
    ListView,\
    RedirectView,\
    UpdateView,\
    CreateView,\
    DeleteView

from .models import User, CollectorKey
from .forms import MyUserCreationForm, MyUserChangeForm, CustomPasswordChangeForm


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
                return self.model.objects.filter(organisation=org, is_superuser=False)



class UserCreate(LoginRequiredMixin, CreateView):
    model = User
    form_class = MyUserCreationForm
    slug_field = "username"
    slug_url_kwarg = "username"

    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation
        return super(UserCreate, self).form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form = MyUserChangeForm
    fields = ['first_name', 'last_name', 'email', 'inspinia_skin', 'organisation_manager', 'organisation']

    def form_valid(self, form):
        print "Form valid for update"
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if self.request.user.organisation_manager:
            if self.request.user.id == form.instance.id:
                form.instance.organisation_manager =  True

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


def new_collector_key(request):
    org = request.user.organisation
    create = request.POST['create']
    if create in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        create = True
    try:

        if create == True:
            org.collectorkey_set.all().delete()
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


def build_collector_key_view(ck):
    res = ' <li class="list-group-item">\
    {0}</li>'.format(ck.collector_key)
    return res
