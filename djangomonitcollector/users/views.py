# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import uuid

from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .models import User, CollectorKey


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['name', 'bootstrap_theme', 'dygraph_color_palette']

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"


def new_collector_key(request):
    user_id = request.user.id
    create = request.POST['create']
    if create in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        create = True
    try:
        user = User.objects.get(pk=user_id)

        if create == True:
            user.collectorkey_set.all().delete()
            CollectorKey.create(uuid.uuid4(), user)
        html = ""
        user_keys = user.collectorkey_set.all()
        for ck in list(user_keys):
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
