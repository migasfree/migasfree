# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import Attribute, MigasLink


@python_2_unicode_compatible
class Policy(models.Model, MigasLink):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True,
        help_text=_("if you uncheck this field, the policy is disabled for"
                    " all computers.")
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        null=True,
        blank=True
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyIncludedAttributes",
        blank=True,
        verbose_name=_("included attributes"),
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyExcludedAttributes",
        blank=True,
        verbose_name=_("excluded attributes"),
    )

    def __str__(self):
        return self.name

    @staticmethod
    def belongs(computer, attributes):
        for attribute in attributes:
            if attribute.id == 1 or \
                    attribute in computer.sync_attributes.all():
                return True

        return False

    @staticmethod
    def belongs_excluding(computer, included_attributes, excluded_attributes):
        if Policy.belongs(computer, included_attributes) and \
                not Policy.belongs(computer, excluded_attributes):
            return True

        return False

    @staticmethod
    def get_packages_to_remove(group):
        _packages = []
        for item in PolicyGroup.objects.filter(policy=group.policy):
            if item.packages_to_install:
                for package in item.packages_to_install.replace("\n", " ").split(" "):
                    if package != "":
                        _packages.append(package)

        for package in group.packages_to_install.replace("\n", " ").split(" "):
            if package != "":
                _packages.remove(package)

        return _packages

    @staticmethod
    def get_packages(computer):
        to_install = []
        to_remove = []

        for policy in Policy.objects.filter(enabled=True):
            if policy.belongs_excluding(
                    computer,
                    policy.included_attributes.all(),
                    policy.excluded_attributes.all()
            ):
                for group in PolicyGroup.objects.filter(policy=policy).order_by("priority"):
                    if policy.belongs_excluding(
                            computer,
                            group.included_attributes.all(),
                            group.excluded_attributes.all()
                    ):
                        if group.packages_to_install:
                            for package in group.packages_to_install.replace("\n", " ").split(" "):
                                if package != "":
                                    to_install.append(package)
                        to_remove.extend(policy.get_packages_to_remove(group))
                        break

        return to_install, to_remove

    class Meta:
        app_label = 'server'
        verbose_name = _("Policy")
        verbose_name_plural = _("Policies")
        unique_together = ("name",)
        permissions = (("can_save_policy", "Can save Policy"),)
        ordering = ['name']


@python_2_unicode_compatible
class PolicyGroup(models.Model, MigasLink):
    priority = models.IntegerField(
        verbose_name=_("priority")
    )

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        verbose_name=_("policy")
    )

    included_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyGroupIncludedAttributes",
        blank=True,
        verbose_name=_("included attributes"),
    )

    excluded_attributes = models.ManyToManyField(
        Attribute,
        related_name="PolicyGroupExcludedAttributes",
        blank=True,
        verbose_name=_("excluded attributes"),
    )

    packages_to_install = models.TextField(
        verbose_name=_("packages to install"),
        null=True,
        blank=True
    )

    def __str__(self):
        return "{}-{}".format(self.policy.name, self.priority)

    class Meta:
        app_label = 'server'
        verbose_name = _("Policy Group")
        verbose_name_plural = _("Policy Groups")
        unique_together = (("policy", "priority"),)
        permissions = (("can_save_policy_group", "Can save Policy Group"),)
        ordering = ['policy__name', 'priority']
