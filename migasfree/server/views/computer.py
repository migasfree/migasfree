# -*- coding: UTF-8 -*-

from datetime import datetime

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from django.utils.translation import ugettext_lazy as _

from ..forms import ComputerReplacementForm
from ..models import (
    Computer, Update, Error, Fault,
    StatusLog, Migration, Login, Version, Repository, FaultDef, DeviceLogical
)
from ..mixins import LoginRequiredMixin
from ..functions import d2s, to_heatmap
from ..api import upload_computer_info


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


@login_required
def computer_simulate_sync(request, pk):
    computer = Computer.objects.get(pk=pk)
    version = Version.objects.get(id=computer.version.id)

    try:
        login = Login.objects.get(computer_id=computer.id)
    except:
        login = None

    if login:
        attributes = {}
        for att in login.attributes.filter(property_att__tag=False):
            attributes[att.property_att.prefix] = att.value

        data = {
            "upload_computer_info": {
                "attributes": attributes,
                "computer": {
                    "user_fullname": login.user.fullname,
                    "pms": version.pms.name,
                    "ip": computer.ip,
                    "hostname": computer.name,
                    "platform": version.platform.name,
                    "version": version.name,
                    "user": login.user.name
                }
            }
        }

        transaction.set_autocommit(False)
        try:
            result = upload_computer_info(
                request,
                computer.name,
                computer.uuid,
                computer,
                data
            )['upload_computer_info.return']
        except:
            result = {}

        transaction.rollback()  # only simulate sync... not real sync!
        transaction.set_autocommit(True)

        result['title'] = _('Simulate sync: %s') % computer.__str__()
        result["computer"] = computer
        result["version"] = version
        result["login"] = login
        result["attributes"] = login.attributes.filter(property_att__tag=False)

        repositories = []
        for repo in result["repositories"]:
            repositories.append(Repository.objects.get(version__id=version.id,name=repo['name']))
        result["repositories"] = repositories

        faultsdef = []
        for fault in result["faultsdef"]:
            faultsdef.append(FaultDef.objects.get(name=fault['name']))
        result["faultsdef"] = faultsdef

        result["default_device"] = result["devices"]["default"]
        devices = []
        for device in result["devices"]["logical"]:
            devices.append(DeviceLogical.objects.get(pk=device['PRINTER']['id']))
        result["devices"] = devices

    else:
        result = {}
        result['title'] = _('Simulate sync: %s') % computer.__str__()
        result["computer"] = computer
        result["version"] = version

        messages.error(
            request,
            _('Error: This computer does not have a login !.')
        )

    return render(
        request,
        'computer_simulate_sync.html',
        result
    )
