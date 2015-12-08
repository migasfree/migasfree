# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class NotificationManager(models.Manager):
    def create(self, notification):
        obj = Notification()
        obj.notification = notification
        obj.save()

        return obj


class Notification(models.Model):
    date = models.DateTimeField(
        verbose_name=_("date"),
        auto_now_add=True
    )

    notification = models.TextField(
        verbose_name=_("notification"),
        null=True,
        blank=True
    )

    checked = models.BooleanField(
        verbose_name=_("checked"),
        default=False,
    )

    objects = NotificationManager()

    def okay(self):
        self.checked = True
        self.save()

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
