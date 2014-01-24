# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.common import link
from migasfree.server.models.computer import Computer
from migasfree.server.models import User, Attribute


class Login(models.Model):
    date = models.DateTimeField(
        _("date"),
        default=0
    )

    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    user = models.ForeignKey(
        User,
        verbose_name=_("user")
    )

    attributes = models.ManyToManyField(
        Attribute,
        null=True,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Sent attributes")
    )

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def user_link(self):
        return self.user.link()

    user_link.allow_tags = True
    user_link.short_description = _("User")

    def __unicode__(self):
        return u'%s@%s' % (
            self.user.name,
            self.computer.__unicode__()
        )

    class Meta:
        app_label = 'server'
        verbose_name = _("Login")
        verbose_name_plural = _("Logins")
        unique_together = (("computer",),)
        permissions = (("can_save_login", "Can save Login"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
