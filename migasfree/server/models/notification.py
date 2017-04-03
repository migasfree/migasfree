# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


class NotificationManager(models.Manager):
    def create(self, message):
        obj = Notification()
        obj.message = message
        obj.save()

        return obj


@python_2_unicode_compatible
class Notification(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("date"),
    )

    message = models.TextField(
        verbose_name=_("message"),
    )

    checked = models.BooleanField(
        verbose_name=_("checked"),
        default=False,
    )

    objects = NotificationManager()

    def checked_ok(self):
        self.checked = True
        self.save()

    @staticmethod
    def unchecked_count():
        return Notification.objects.filter(checked=0).count()

    def save(self, *args, **kwargs):
        self.message = self.message.replace("\r\n", "\n")
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ({:%Y-%m-%d %H:%M:%S})'.format(self.id, self.created_at)

    class Meta:
        app_label = 'server'
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        permissions = (("can_save_notification", "Can save Notification"),)
