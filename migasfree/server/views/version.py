# -*- coding: UTF-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import DeleteView
from django.utils.translation import ugettext_lazy as _

from ..models import Project
from ..mixins import LoginRequiredMixin


class ProjectDelete(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    context_object_name = 'project'
    success_url = reverse_lazy('admin:server_project_changelist')

    def get_success_url(self):
        messages.success(self.request, _("Project %s deleted!") % self.object)
        return self.success_url
