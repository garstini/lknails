from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_homepage_returns_ok(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_services_page_returns_ok(self):
        response = self.client.get(reverse("service_list"))
        self.assertEqual(response.status_code, 200)

    def test_gallery_page_returns_ok(self):
        response = self.client.get(reverse("gallery"))
        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_ok(self):
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)
