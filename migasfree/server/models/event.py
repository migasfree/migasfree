# -*- coding: utf-8 -*-

# Copyright (c) 2016-2017 Jose Antonio Chavarría <jachavar@gmail.com>
# Copyright (c) 2016-2017 Alberto Gacías <alberto@migasfree.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.db.models.aggregates import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from .computer import Computer


@python_2_unicode_compatible
class Event(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('date')
    )

    computer = models.ForeignKey(
        Computer,
        on_delete=models.CASCADE,
        verbose_name=_("computer")
    )

    @classmethod
    def by_day(cls, computer_id, start_date, end_date):
        return cls.objects.filter(
             computer__id=computer_id,
             created_at__range=(start_date, end_date)
        ).extra(
            {"day": "date_trunc('day', created_at)"}
        ).values('day').annotate(count=Count('id')).order_by('-day')

    @classmethod
    def by_hour(cls, start_date, end_date):
        return cls.objects.filter(
            created_at__range=(start_date, end_date)
        ).extra(
            {"hour": "date_trunc('hour', created_at)"}
        ).values('hour').annotate(
            count=Count('computer_id', distinct=True)
        ).order_by('hour')

    def __str__(self):
        return u'{} ({:%Y-%m-%d %H:%M:%S})'.format(self.computer, self.created_at)

    class Meta:
        abstract = True
