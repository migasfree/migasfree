# -*- coding: utf-8 -*-

# http://docs.djangoproject.com/en/dev/topics/testing/
# http://okkum.wordpress.com/2009/02/16/testing-con-django-mas-alla-de-unittest/

import os
import settings
from datetime import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from migasfree.server.models import *
from migasfree.server.fixtures import create_registers


class RepositoryTestCase(TransactionTestCase):
    def setUp(self):  # pylint: disable-msg=C0103
        create_registers()
        p=Platform()
        p.name = "Linux"
        p.save()

        version = Version()
        version.name = "UBUNTU"
        version.pms =  Pms.objects.get(name="apt-get")
        version.platform = Platform.objects.get(name="Linux")
        version.save()

        self.test1 = Repository()
        self.test1.name = "TEST 1 2"
        self.test1.active = True
        self.test1.version = version
        self.test1.date = datetime.now().date()
#        self.test1.schedule = Schedule.objects.get(name="STANDARD")
        self.test1.toinstall = "bluefish"
        self.test1.toremove = ""
        self.test1.save()


# WARNING: the following methods must start with "test"
    def test_repository_name(self):
        self.assertEqual(self.test1.name, 'TEST_1_2')


    def test_login_site(self):
        result = self.client.login(username='admin', password='admin')
        self.assertEqual(result, True)

        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('admin:server_repository_changelist')
        )
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 1 repository.
        self.assertEqual(
            response.context['selection_note_all'],
            "1 selected"
        )
