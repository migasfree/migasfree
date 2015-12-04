# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models.computer import Computer
from . import User, Attribute, MigasLink


class LoginManager(models.Manager):
    def create(self, computer, user, attributes=None):
        login = Login()
        login.computer = computer
        login.user = user
        login.attributes = attributes
        login.save()

        return login


class Login(models.Model, MigasLink):
    date = models.DateTimeField(
        verbose_name=_("date"),
        auto_now_add=True
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
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Sent attributes")
    )

    objects = LoginManager()

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
