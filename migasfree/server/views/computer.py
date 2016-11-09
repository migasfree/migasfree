# -*- coding: UTF-8 -*-

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from django.utils.translation import ugettext_lazy as _

from ..forms import ComputerReplacementForm
from ..models import Computer, Update, Error, Fault, StatusLog, Migration
from ..mixins import LoginRequiredMixin
from ..functions import d2s, to_heatmap


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
        computer_ids = selected.split(', ')
        deleted = []
        for item in computer_ids:
            try:
                computer = Computer.objects.get(pk=int(item))
                deleted.append(computer.__str__())
                computer.delete()
            except ObjectDoesNotExist:
                pass

        messages.success(
            request,
            _("Computers %s, deleted!") % ', '.join([x for x in deleted])
        )

    return redirect(success_url)


@login_required
def computer_change_status(request):
    success_url = reverse_lazy('admin:server_computer_changelist')

    selected = request.POST.get('selected', None)
    status = request.POST.get('status', None)
    if selected and status:
        computer_ids = selected.split(', ')
        changed = []
        for item in computer_ids:
            try:
                computer = Computer.objects.get(pk=int(item))
                computer.change_status(status)
                changed.append(computer.__str__())
            except ObjectDoesNotExist:
                pass

        messages.success(
            request,
            _("Computers %s, changed status!") % ', '.join([x for x in changed])
        )

    return redirect(success_url)


@login_required
def computer_replacement(request):
    if request.method == 'POST':
        form = ComputerReplacementForm(request.POST)
        if form.is_valid():
            source = get_object_or_404(
                Computer, pk=form.cleaned_data.get('source').pk
            )
            target = get_object_or_404(
                Computer, pk=form.cleaned_data.get('target').pk
            )
            Computer.replacement(source, target)

            messages.success(request, _('Replacement done.'))
            messages.info(
                request,
                '<br/>'.join(sorted(d2s(source.get_replacement_info())))
            )
            messages.info(
                request,
                '<br/>'.join(sorted(d2s(target.get_replacement_info())))
            )

            return HttpResponseRedirect(reverse('computer_replacement'))
    else:
        form = ComputerReplacementForm()

    return render(
        request,
        'computer_replacement.html',
        {
            'title': _('Computers Replacement'),
            'form': form
        }
    )


@login_required
def computer_events(request, pk):
    computer = get_object_or_404(Computer, pk=pk)
    now = datetime.now()

    updates = to_heatmap(
        Update.by_day(computer.pk, computer.dateinput, now)
    )
    updates_count = sum(updates.values())

    errors = to_heatmap(
        Error.by_day(computer.pk, computer.dateinput, now)
    )
    errors_count = sum(errors.values())

    faults = to_heatmap(
        Fault.by_day(computer.pk, computer.dateinput, now)
    )
    faults_count = sum(faults.values())

    status = to_heatmap(
        StatusLog.by_day(computer.pk, computer.dateinput, now)
    )
    status_count = sum(status.values())

    migrations = to_heatmap(
        Migration.by_day(computer.pk, computer.dateinput, now)
    )
    migrations_count = sum(migrations.values())

    return render(
        request,
        'computer_events.html',
        {
            'title': '{}: {}'.format(_('Events'), computer.__str__()),
            'computer': computer,
            'updates': updates,
            'updates_count': updates_count,
            'errors': errors,
            'errors_count': errors_count,
            'faults': faults,
            'faults_count': faults_count,
            'status': status,
            'status_count': status_count,
            'migrations': migrations,
            'migrations_count': migrations_count,
        }
    )
