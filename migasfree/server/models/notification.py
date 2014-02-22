# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Notification(models.Model):

    date = models.DateTimeField(
        _("date"),
        default=0
    )

    notification = models.TextField(
        _("notification"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        _("checked"),
        default=False,
    )

    def save(self, *args, **kwargs):
        self.notification = self.notification.replace("\r\n", "\n")
        super(Notification, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s - %s' % (
            str(self.id),
            str(self.date)
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        permissions = (("can_save_notification", "Can save Notification"),)
