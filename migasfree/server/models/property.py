# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import LANGUAGES_CHOICES, MigasLink


class ClientPropertyManager(models.Manager):
    def get_queryset(self):
        return super(ClientPropertyManager, self).get_queryset().filter(
            tag=False
        )


class TagTypeManager(models.Manager):
    def get_queryset(self):
        return super(TagTypeManager, self).get_queryset().filter(
            tag=True
        )


@python_2_unicode_compatible
class Property(models.Model, MigasLink):
    KIND_CHOICES = (
        ('N', _('NORMAL')),
        ('-', _('LIST')),
        ('L', _('ADDS LEFT')),
        ('R', _('ADDS RIGHT')),
    )

    PREFIX_LEN = 3

    prefix = models.CharField(
        verbose_name=_("prefix"),
        max_length=PREFIX_LEN,
        unique=True
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    language = models.IntegerField(
        verbose_name=_("programming language"),
        default=1,
        choices=LANGUAGES_CHOICES
    )

    code = models.TextField(
        verbose_name=_("Code"),
        null=False,
        blank=True,
        help_text=_("This code will execute in the client computer, "
                    "and it must put in the standard output the value of the "
                    "attribute correspondent to this property.<br>"
                    "The format of this value is 'name~description', "
                    "where 'description' is optional.<br>"
                    "<b>Example of code:</b><br>"
                    "#Create a attribute with the name of computer from bash"
                    "<br> echo $HOSTNAME")
    )

    active = models.BooleanField(
        verbose_name=_("active"),
        default=True,
    )

    kind = models.CharField(
        verbose_name=_("kind"),
        max_length=1,
        default="N",
        choices=KIND_CHOICES
    )

    auto = models.BooleanField(
        verbose_name=_("auto"),
        default=True,
        help_text=_("automatically add the attribute to database")
    )

    tag = models.BooleanField(
        verbose_name=_("tag"),
        default=False,
        help_text=_("tag")
    )

    def namefunction(self):
        return "PROPERTY_%s" % self.prefix

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.replace("\r\n", "\n")
        super(Property, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Not allowed delete SET and CID Property
        if self.prefix not in ["SET", "CID"]:
            super(Property, self).delete(*args, **kwargs)

    @staticmethod
    def enabled_client_properties():
        return Property.objects.filter(active=True, tag=False).exclude(
            prefix="CID"
        ).values('language', 'prefix', 'code')

    class Meta:
        app_label = 'server'
        verbose_name = _("Property/TagType")
        verbose_name_plural = _("Properties/TagTypes")
        permissions = (("can_save_property", "Can save Property"),)
        ordering = ['name']


class ClientProperty(Property):
    objects = ClientPropertyManager()

    def save(self, *args, **kwargs):
        self.tag = False
        super(ClientProperty, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        proxy = True


class TagType(Property):
    objects = TagTypeManager()

    def save(self, *args, **kwargs):
        self.tag = True
        super(TagType, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("Tag Type")
        verbose_name_plural = _("Tag Types")
        proxy = True
