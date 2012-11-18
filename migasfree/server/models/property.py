# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from common import link, LANGUAGES_CHOICES


class Property(models.Model):
    KIND_CHOICES = (
        ('N', unicode(_('NORMAL'))),
        ('-', unicode(_('LIST'))),
        ('L', unicode(_('ADDS LEFT'))),
        ('R', unicode(_('ADDS RIGHT'))),
    )

    prefix = models.CharField(
        unicode(_("prefix")),
        max_length=3,
        unique=True
    )

    name = models.CharField(
        unicode(_("name")),
        max_length=50
    )

    language = models.IntegerField(
        unicode(_("programming language")),
        default=0,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        unicode(_("Code")),
        null=False,
        blank=True,
        help_text=unicode(_("This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of computer from bash<br> echo $HOSTNAME"))
    )

    before_insert = models.TextField(
        unicode(_("before insert")),
        null=False,
        blank=True,
        help_text=unicode(_("Code django. This code will execute before insert the attribute in the server. You can modify the value of attribute here, using the variable 'data'."))
    )

    after_insert = models.TextField(
        unicode(_("after insert")),
        null=False,
        blank=True,
        help_text=unicode(_("Code django. This code will execute after insert the attribute in the server."))
    )

    active = models.BooleanField(
        unicode(_("active")),
        default=True,
        help_text=""
    )

    kind = models.CharField(
        unicode(_("kind")),
        max_length=1,
        default="N",
        choices=KIND_CHOICES
    )

    auto = models.BooleanField(
        unicode(_("auto")),
        default=True,
        help_text="automatically add the attribute to database"
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
        verbose_name = unicode(_("Property"))
        verbose_name_plural = unicode(_("Properties"))
        permissions = (("can_save_property", "Can save Property"),)

    def link(self):
        return link(self, self._meta.object_name)

    link.short_description = Meta.verbose_name
    link.allow_tags = True
