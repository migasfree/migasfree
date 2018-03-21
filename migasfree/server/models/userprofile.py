# -*- coding: utf-8 -*-

from django.db import models, connection

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (
    User as UserSystem,
    UserManager
)

from .common import MigasLink


class UserProfile(UserSystem, MigasLink):
    domains = models.ManyToManyField(
        'Domain',
        blank=True,
        verbose_name=_("domains"),
        related_name='domains'
    )

    domain_preference = models.ForeignKey(
        'Domain',
        blank=True,
        verbose_name=_("domain"),
        null=True,
        on_delete=models.SET_NULL
    )

    scope_preference = models.ForeignKey(
        'Scope',
        blank=True,
        verbose_name=_("Scope"),
        null=True,
        on_delete=models.SET_NULL
    )

    objects = UserManager()

    def is_view_all(self):
        if str(self) == "AnonymousUser":
            # TODO: only view current computer (migasfree-client 4.x)
            return True
        else:
            return not self.domain_preference and not self.scope_preference

    def get_computers(self):
        cursor = connection.cursor()
        ctx = {"domain": self.domain_preference_id, 'scope': self.scope_preference_id}

        if self.domain_preference:
            sql_domain = """
(
SELECT distinct computer_id  from server_computer_sync_attributes
WHERE attribute_id IN ( SELECT attribute_id
FROM server_domain_included_attributes WHERE domain_id = %(domain)s )
EXCEPT
SELECT distinct computer_id  from server_computer_sync_attributes
WHERE attribute_id IN ( SELECT attribute_id
FROM server_domain_excluded_attributes WHERE domain_id = %(domain)s)
)
""" % ctx
        else:
            sql_domain = ""

        if self.scope_preference:
            sql_scope = """
(
SELECT distinct computer_id  from server_computer_sync_attributes
WHERE attribute_id IN ( SELECT attribute_id
FROM server_scope_included_attributes WHERE scope_id = %(scope)s )
EXCEPT
SELECT distinct computer_id  from server_computer_sync_attributes
WHERE attribute_id IN ( SELECT attribute_id
FROM server_scope_excluded_attributes WHERE scope_id = %(scope)s )
)
""" % ctx
        else:
            sql_scope = ""

        sql = """
SELECT ARRAY(
%(sql_domain)s
%(operator)s
%(sql_scope)s
)
""" % {
            'sql_domain': sql_domain,
            'sql_scope': sql_scope,
            'operator': " INTERSECT" if (self.domain_preference and self.scope_preference) else ""
        }

        cursor.execute(sql)
        computers = cursor.fetchall()[0][0]
        cursor.close()

        return computers

    def get_attributes(self):
        attributes = []
        computers = self.get_computers()
        if computers:
            cursor = connection.cursor()
            cursor.execute("""
                select array(
                    select DISTINCT attribute_id from server_computer_sync_attributes WHERE computer_id IN %s
                ) as attributes""" % ("(" + ",".join(str(e) for e in computers) + ")") )
            attributes = cursor.fetchall()[0][0]
            cursor.close()

        return attributes

    def get_domain_tags(self):
        tags = []
        if self.domain_preference:

            cursor = connection.cursor()
            cursor.execute("""
                select array(
                    select serverattribute_id from server_domain_tags where domain_id=%s
                ) as attributes """ % (self.domain_preference.id))
            tags = cursor.fetchall()[0][0]
            cursor.close()
        return tags

    def get_projects(self):
        projects = []
        cursor = connection.cursor()
        computers = self.get_computers()
        if computers:
            cursor.execute("""
                select array(
                    select DISTINCT project_id from server_computer WHERE id IN %s
                ) as projects""" % ("(" + ",".join(str(e) for e in computers) + ")")
            )
            projects = cursor.fetchall()[0][0]
            cursor.close()

        return projects

    def update_scope(self, value):
        self.scope_preference = value if value > 0 else None
        self.save()

    def update_domain(self, value):
        self.domain_preference = value if value > 0 else None
        self.save()

    def save(self, *args, **kwargs):
        if not (
            self.password.startswith("sha1$")
            or self.password.startswith("pbkdf2")
        ):
            super(UserProfile, self).set_password(self.password)

        super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        app_label = 'server'
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        permissions = (("can_save_userprofile", "Can save User Profile"),)
