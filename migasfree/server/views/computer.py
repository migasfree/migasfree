# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ..models import Computer


class LoginRequiredMixin(object):
    # https://code.djangoproject.com/ticket/16626

    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class ComputerDelete(LoginRequiredMixin, DeleteView):
    model = Computer
    template_name = 'computer_confirm_delete.html'
    context_object_name = 'computer'
    success_url = reverse_lazy('admin:server_computer_changelist')

    def get_success_url(self):
        messages.success(self.request, _("Computer %s deleted!") % self.object)
        return self.success_url


@login_required
def computer_delete_selected(request):
    success_url = reverse_lazy('admin:server_computer_changelist')

    selected = request.POST.get('selected', None)
    if selected:
        objects = selected.split(', ')
        for item in objects:
            computer = Computer.objects.get(
                **{settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0]: item}
            )
            computer.delete()

        messages.success(request, _("Computers %s deleted!") % selected)

    return redirect(success_url)
