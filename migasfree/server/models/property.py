# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import MigasLink


class ClientPropertyManager(models.Manager):
    def get_queryset(self):
        return super(ClientPropertyManager, self).get_queryset().filter(
            sort='client'
        )


class ServerPropertyManager(models.Manager):
    def get_queryset(self):
        return super(ServerPropertyManager, self).get_queryset().filter(
            sort='server'
        )


@python_2_unicode_compatible
class Property(models.Model, MigasLink):
    SORT_CHOICES = (
        ('basic', _('Basic')),
        ('client', _('Client')),
        ('server', _('Server')),
    )

    KIND_CHOICES = (
        ('N', _('Normal')),
        ('-', _('List')),
        ('L', _('Added to the left')),
        ('R', _('Added to the right')),
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

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True,
    )

    kind = models.CharField(
        verbose_name=_("kind"),
        max_length=1,
        default='N',
        choices=KIND_CHOICES
    )

    sort = models.CharField(
        verbose_name=_("sort"),
        max_length=10,
        default='client',
        choices=SORT_CHOICES
    )

    auto_add = models.BooleanField(
        verbose_name=_("automatically add"),
        default=True,
        help_text=_("automatically add the attribute to database")
    )

    language = models.IntegerField(
        verbose_name=_("programming language"),
        default=settings.MIGASFREE_PROGRAMMING_LANGUAGES[0][0],
        choices=settings.MIGASFREE_PROGRAMMING_LANGUAGES
    )

    code = models.TextField(
        verbose_name=_("code"),
        null=True,
        blank=True,
        help_text=_("This code will execute in the client computer, and it must"
                    " put in the standard output the value of the attribute correspondent"
                    " to this property.<br>The format of this value is 'name~description',"
                    " where 'description' is optional.<br><b>Example of code:</b>"
                    "<br>#Create an attribute with the name of computer from bash<br>"
                    " echo $HOSTNAME")
    )

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        # Not allowed delete basic properties
        if self.sort != 'basic':
            return super(Property, self).delete(using, keep_parents)

    @staticmethod
    def enabled_client_properties():
        client_properties = []
        for item in Property.objects.filter(enabled=True, sort='client'):
            client_properties.append({
                "language": item.get_language_display(),
                "name": item.prefix,
                "code": item.code
            })

        return client_properties

    class Meta:
        app_label = 'server'
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        permissions = (("can_save_property", "Can save Property"),)
        ordering = ['name']


class ServerProperty(Property):
    objects = ServerPropertyManager()

    def save(self, *args, **kwargs):
        self.sort = 'server'
        self.code = ''
        super(ServerProperty, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Tag Category")
        verbose_name_plural = _("Tag Categories")
        proxy = True


class ClientProperty(Property):
    objects = ClientPropertyManager()

    def save(self, *args, **kwargs):
        self.sort = 'client'
        self.code = self.code.replace("\r\n", "\n")
        super(ClientProperty, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Formula")
        verbose_name_plural = _("Formulas")
        proxy = True


class BasicProperty(Property):
    def save(self, *args, **kwargs):
        self.sort = 'basic'
        self.code = self.code.replace("\r\n", "\n")
        super(BasicProperty, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Basic Property")
        verbose_name_plural = _("Basic Properties")
        proxy = True
