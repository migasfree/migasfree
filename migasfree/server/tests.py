# -*- coding: utf-8 -*-

# http://docs.djangoproject.com/en/dev/topics/testing/
# http://okkum.wordpress.com/2009/02/16/testing-con-django-mas-alla-de-unittest/

from datetime import datetime

from django.test import TransactionTestCase
from django.urls import reverse

from .models import InternalSource, Platform, Project, Pms
from .fixtures import create_initial_data, sequence_reset


class InternalSourceTestCase(TransactionTestCase):
    def setUp(self):  # pylint: disable-msg=C0103
        create_initial_data()
        sequence_reset()

        platform = Platform.objects.create("Linux")

        project = Project.objects.create(
            "UBUNTU",
            Pms.objects.get(name="apt-get"),
            platform
        )

        self.test1 = InternalSource()
        self.test1.name = "TEST 1 2"
        self.test1.enabled = True
        self.test1.project = project
        self.test1.start_date = datetime.now().date()
        self.test1.packages_to_install = "bluefish"
        self.test1.packages_to_remove = ""
        self.test1.save()  # FIXME remove

    def test_name(self):
        self.assertEqual(self.test1.name, 'test-1-2')

    def test_login(self):
        result = self.client.login(username='admin', password='admin')
        self.assertEqual(result, True)

        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('admin:server_internalsource_changelist')
        )
        self.assertEqual(response.status_code, 200)
