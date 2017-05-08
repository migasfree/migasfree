# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.utils.translation import ugettext_lazy as _

from ..models import Platform


class PlatformDelete(LoginRequiredMixin, DeleteView):
    model = Platform
    template_name = 'platform_confirm_delete.html'
    context_object_name = 'platform'
    success_url = reverse_lazy('admin:server_platform_changelist')

    def get_success_url(self):
        messages.success(self.request, _("Platform %s deleted!") % self.object)
        return self.success_url


@login_required
def platform_delete_selected(request):
    success_url = reverse_lazy('admin:server_platform_changelist')

    selected = request.POST.get('selected', None)
    if selected:
        objects = selected.split(', ')
        for item in objects:
            Platform.objects.filter(name=item).delete()

        messages.success(request, _("Platforms %s deleted!") % selected)

    return redirect(success_url)
