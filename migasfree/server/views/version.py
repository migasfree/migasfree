# -*- coding: UTF-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import DeleteView
from django.utils.translation import ugettext_lazy as _

from ..models import Version
from ..mixins import LoginRequiredMixin


class VersionDelete(LoginRequiredMixin, DeleteView):
    model = Version
    template_name = 'version_confirm_delete.html'
    context_object_name = 'version'
    success_url = reverse_lazy('admin:server_version_changelist')

    def get_success_url(self):
        messages.success(self.request, _("Version %s deleted!") % self.object)
        return self.success_url
