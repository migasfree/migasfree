# http://docs.djangoproject.com/en/dev/topics/testing/
# http://okkum.wordpress.com/2009/02/16/testing-con-django-mas-alla-de-unittest/

# to create fixture: ./manage.py dumpdata>test.json
# To run execute: ./manage.py test

from migasfree.system.models import *
from datetime import datetime
from django.test import TestCase
from django.test.client import Client


class RepositoryTestCase(TestCase):
    fixtures = ['/srv/Django/migasfree/test.json',]

    def setUp(self):

        self.test1 = Repository()
        self.test1.name="TEST 1 2"
        self.test1.active=True
        self.test1.version=Version.objects.get(name="UBUNTU")
        self.test1.date=datetime.now().date()
        self.test1.schedule=Schedule.objects.get(name="STANDARD")
        self.test1.toinstall="bluefish"
        self.test1.toremove=""
        self.test1.save()
#        self.test1.packages.add(oPackage)
        self.test1.attributes.add(Attribute.objects.get(value="RYS.AYTOZAR"))
        self.test1.save()



# WARNING: the following methods must start with "test"
    def test_RepositoryName(self):
        self.assertEquals(self.test1.name, 'TEST_1_2')

    def test_LoginSite(self):
        result=self.client.login(username='admin', password='admin')
        self.assertEquals(result,True)
        response = self.client.get('/migasfree/admin/')
        self.assertEquals(response.status_code, 200) 
        
        # Issue a GET request.
        response = self.client.get('/migasfree/admin/system/repository/')

        # Check that the response is 200 OK.
        self.failUnlessEqual(response.status_code, 200)

#        # Check that the rendered context contains 2 repositories.
#        print response.context
#        self.failUnlessEqual(response.context['selection_note_all'], "2 Repositories")






