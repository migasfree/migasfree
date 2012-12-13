# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from common import link, LANGUAGES_CHOICES


class Property(models.Model):
    KIND_CHOICES = (
        ('N', _('NORMAL')),
        ('-', _('LIST')),
        ('L', _('ADDS LEFT')),
        ('R', _('ADDS RIGHT')),
    )

    prefix = models.CharField(
        _("prefix"),
        max_length=3,
        unique=True
    )

    name = models.CharField(
        _("name"),
        max_length=50
    )

    language = models.IntegerField(
        _("programming language"),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        _("Code"),
        null=False,
        blank=True,
        help_text=_("This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of computer from bash<br> echo $HOSTNAME")
    )

    before_insert = models.TextField(
        _("before insert"),
        null=False,
        blank=True,
        help_text=_("Code django. This code will execute before insert the attribute in the server. You can modify the value of attribute here, using the variable 'data'.")
    )

    after_insert = models.TextField(
        _("after insert"),
        null=False,
        blank=True,
        help_text=_("Code django. This code will execute after insert the attribute in the server.")
    )

    active = models.BooleanField(
        _("active"),
        default=True,
    )

    kind = models.CharField(
        _("kind"),
        max_length=1,
        default="N",
        choices=KIND_CHOICES
    )

    auto = models.BooleanField(
        _("auto"),
        default=True,
        help_text=_("automatically add the attribute to database")
    )

    def namefunction(self):
        return "PROPERTY_%s" % self.prefix

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        self.before_insert = self.before_insert.replace("\r\n", "\n")
        self.after_insert = self.after_insert.replace("\r\n", "\n")
        super(Property, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        permissions = (("can_save_property", "Can save Property"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
