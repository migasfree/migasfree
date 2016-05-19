# -*- coding: utf-8 -*-

# http://docs.djangoproject.com/en/dev/topics/testing/
# http://okkum.wordpress.com/2009/02/16/testing-con-django-mas-alla-de-unittest/

from datetime import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from .models import *
from .fixtures import create_registers, sequence_reset


class RepositoryTestCase(TransactionTestCase):
    def setUp(self):  # pylint: disable-msg=C0103
        create_registers()
        sequence_reset()

        platform = Platform.objects.create("Linux")

        version = Version.objects.create(
            "UBUNTU",
            Pms.objects.get(name="apt-get"),
            platform
        )

        self.test1 = Repository()
        self.test1.name = "TEST 1 2"
        self.test1.active = True
        self.test1.version = version
        self.test1.date = datetime.now().date()
        self.test1.toinstall = "bluefish"
        self.test1.toremove = ""
        self.test1.save()  # FIXME remove

    def test_repository_name(self):
        self.assertEqual(self.test1.name, 'test-1-2')

    def test_login_site(self):
        result = self.client.login(username='admin', password='admin')
        self.assertEqual(result, True)

        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('admin:server_repository_changelist')
        )
        self.assertEqual(response.status_code, 200)
