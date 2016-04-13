# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone, dateformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .computer import Computer
from . import User, Attribute, MigasLink


class LoginManager(models.Manager):
    def create(self, computer, user, attributes=None):
        obj = Login()
        obj.computer = computer
        obj.user = user
        obj.attributes = attributes
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


@python_2_unicode_compatible
class Login(models.Model, MigasLink):
    date = models.DateTimeField(
        verbose_name=_("date"),
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
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Sent attributes")
    )

    objects = LoginManager()

    def update_user(self, user):
        self.user = user
        self.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.save()

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    def user_link(self):
        return self.user.link()

    user_link.allow_tags = True
    user_link.short_description = _("User")

    def __str__(self):
        return u'%s (%s)' % (self.user.name, self.user.fullname.strip())

    class Meta:
        app_label = 'server'
        verbose_name = _("Login")
        verbose_name_plural = _("Logins")
        unique_together = (("computer",),)
        permissions = (("can_save_login", "Can save Login"),)
