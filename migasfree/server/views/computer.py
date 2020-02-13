# -*- coding: UTF-8 -*-

from datetime import datetime

from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from ...catalog.models import Policy

from ..forms import ComputerReplacementForm
from ..models import (
    Computer, Synchronization, Error, Fault,
    StatusLog, Migration, Project, Deployment,
    FaultDefinition, DeviceLogical,
    Attribute, AttributeSet,
)
from ..utils import d2s, to_heatmap
from ..api import upload_computer_info


class ComputerDelete(LoginRequiredMixin, DeleteView):
    model = Computer
    template_name = 'computer_confirm_delete.html'
    context_object_name = 'computer'
    success_url = reverse_lazy('admin:server_computer_changelist')

    def get_success_url(self):
        messages.success(self.request, _('Computer %s deleted!') % self.object)

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
            _('Computers %s, deleted!') % ', '.join([x for x in deleted])
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
            _('Computers %s, changed status!') % ', '.join([x for x in changed])
        )

    return redirect(success_url)


@permission_required('server.change_computer', raise_exception=True)
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
            'form': form,
            'help': 'computerreplacement',
        }
    )


@login_required
def computer_events(request, pk):
    computer = get_object_or_404(Computer, pk=pk)
    request.user.userprofile.check_scope(pk)

    now = datetime.now()

    syncs = to_heatmap(
        Synchronization.by_day(computer.pk, computer.created_at, now, request.user.userprofile)
    )
    syncs_count = sum(syncs.values())

    errors = to_heatmap(
        Error.by_day(computer.pk, computer.created_at, now, request.user.userprofile)
    )
    errors_count = sum(errors.values())

    faults = to_heatmap(
        Fault.by_day(computer.pk, computer.created_at, now, request.user.userprofile)
    )
    faults_count = sum(faults.values())

    status = to_heatmap(
        StatusLog.by_day(computer.pk, computer.created_at, now, request.user.userprofile)
    )
    status_count = sum(status.values())

    migrations = to_heatmap(
        Migration.by_day(computer.pk, computer.created_at, now, request.user.userprofile)
    )
    migrations_count = sum(migrations.values())

    return render(
        request,
        'computer_events.html',
        {
            'title': '{}: {}'.format(_('Events'), computer),
            'computer': computer,
            'syncs': syncs,
            'syncs_count': syncs_count,
            'errors': errors,
            'errors_count': errors_count,
            'faults': faults,
            'faults_count': faults_count,
            'status': status,
            'status_count': status_count,
            'migrations': migrations,
            'migrations_count': migrations_count,
            'help': 'computerevents',
        }
    )


def pack_attributes(attributes):
    """
    :param attributes: queryset with structure property_att__prefix, property_att__kind, value
    :return: dict with property_att__prefix as key and packed values as value
    """
    packed = dict()
    for att in attributes:
        if att[0] in packed:
            if att[1] == '-':  # list
                packed[att[0]] = '{},{}'.format(packed[att[0]], att[2])
            elif att[1] == 'L' or att[1] == 'R':  # add to left or right
                if len(att[2]) > len(packed[att[0]]):
                    packed[att[0]] = att[2]
        else:
            packed[att[0]] = att[2]

    return packed


@login_required
def computer_simulate_sync(request, pk):
    user = request.user
    computer = get_object_or_404(Computer, pk=pk)
    user.userprofile.check_scope(pk)
    project = Project.objects.get(id=computer.project.id)

    # do not use the logged user. Change to AnonymousUser
    request.user = AnonymousUser()

    result = {
        'title': _('Simulate sync: %s') % computer,
        'computer': computer,
        'project': project,
        'help': 'computersimulatesync',
    }

    if computer.status == 'unsubscribed':
        messages.error(
            request,
            _('Error: This computer, with unsubscribed status, is not allowed to synchronize!')
        )
    else:
        if not computer.sync_user:
            messages.error(
                request,
                _('Error: This computer does not have any synchronization!')
            )
        else:
            data = {
                'upload_computer_info': {
                    'attributes': pack_attributes(
                        computer.sync_attributes.values_list(
                            'property_att__prefix', 'property_att__kind', 'value'
                        )
                    ),
                    'computer': {
                        'user_fullname': computer.sync_user.fullname,
                        'pms': project.pms.name,
                        'ip': computer.ip_address,
                        'hostname': computer.name,
                        'platform': project.platform.name,
                        'project': project.name,
                        'user': computer.sync_user.name
                    }
                }
            }

            transaction.set_autocommit(False)
            try:
                computer_info_result = upload_computer_info(
                    request,
                    computer.name,
                    computer.uuid,
                    computer,
                    data
                )['upload_computer_info.return']
            except:
                computer_info_result = {}

            result.update(computer_info_result)

            transaction.rollback()  # only simulate sync... not real sync!
            transaction.set_autocommit(True)

            result['attributes'] = computer.sync_attributes.filter(
                property_att__sort='client'
            )

            set_ids = AttributeSet.process(
                [1, computer.get_cid_attribute().id] +
                list(computer.tags.values_list('id', flat=True)) +
                list(result['attributes'].values_list('id', flat=True))
            )

            result['sets'] = Attribute.objects.filter(id__in=[1] + set_ids)  # FIXME constant

            result['repositories'] = Deployment.objects.filter(
                project__id=project.id,
                name__in=[item['name'] for item in result.get('repositories', []) if 'name' in item]
            )

            result['faultsdef'] = FaultDefinition.objects.filter(
                name__in=[item['name'] for item in result.get('faultsdef', []) if 'name' in item]
            )

            result['default_device'] = result.get('devices', {}).get('default', 0)
            devices = []
            for device in result.get('devices', {}).get('logical', []):
                devices.append(DeviceLogical.objects.get(pk=device['PRINTER']['id']))
            result['devices'] = devices

            policy_pkg_to_install, policy_pkg_to_remove = Policy.get_packages(computer)
            result['policies'] = {'to_install': policy_pkg_to_install, 'to_remove': policy_pkg_to_remove}

            request.user = user  # return to logged user

    return render(
        request,
        'computer_simulate_sync.html',
        result
    )
