# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import LANGUAGES_CHOICES, MigasLink


class Property(models.Model, MigasLink):
    KIND_CHOICES = (
        ('N', _('NORMAL')),
        ('-', _('LIST')),
        ('L', _('ADDS LEFT')),
        ('R', _('ADDS RIGHT')),
    )

    PREFIX_LEN = 3

    prefix = models.CharField(
        _("prefix"),
        max_length=PREFIX_LEN,
        unique=True
    )

    name = models.CharField(
        _("name"),
        max_length=50
    )

    language = models.IntegerField(
        _("programming language"),
        default=1,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        _("Code"),
        null=False,
        blank=True,
        help_text=_("This code will execute in the client computer, and it must put in the standard output the value of the attribute correspondent to this property.<br>The format of this value is 'name~description', where 'description' is optional.<br><b>Example of code:</b><br>#Create a attribute with the name of computer from bash<br> echo $HOSTNAME")
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

    tag = models.BooleanField(
        _("tag"),
        default=False,
        help_text=_("tag")
    )

    def namefunction(self):
        return "PROPERTY_%s" % self.prefix

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        super(Property, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Not allowed delete CID and ALL Property
        if self.prefix != "CID" and self.prefix != "ALL":
            super(Property, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        permissions = (("can_save_property", "Can save Property"),)


class KindTag(Property):
    _exclude_links = ["attribute - property_att", ]
    _include_links = ["tag - property_att", ]

    def save(self, *args, **kwargs):
        self.tag = True
        super(KindTag, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Kind Tag")
        verbose_name_plural = _("Kinds Tag")
        proxy = True
