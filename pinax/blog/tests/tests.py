from django.test import TestCase, override_settings

from pinax.blog.utils import get_current_site


class Tests(TestCase):

    @override_settings(CURRENT_SITE=None)
    def test_get_current_site(self):
        site = get_current_site()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')

    def test_get_current_site_from_settings(self):
        site = get_current_site()
        self.assertEqual(site.name, 'Test site')
        self.assertEqual(site.domain, 'http://test.example.com/')
