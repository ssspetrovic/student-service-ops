from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from accounts.models import User


def test_health_endpoint_returns_ok():
    response = Client().get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_jwt_token_urls_are_registered():
    assert reverse("token_obtain_pair") == "/api/auth/token/"
    assert reverse("token_refresh") == "/api/auth/token/refresh/"
    assert reverse("token_logout") == "/api/auth/logout/"
    assert reverse("csrf-cookie") == "/api/auth/csrf/"


class CookieRefreshSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="session@example.com",
            password="StrongPassword123!",
        )
        self.client = Client(enforce_csrf_checks=True)

    def login(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "StrongPassword123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_login_returns_only_access_token_and_sets_refresh_cookie(self):
        response = self.login()

        self.assertEqual(set(response.json()), {"access"})
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertEqual(cookie["path"], "/api/auth/")
        self.assertEqual(cookie["max-age"], settings.JWT_REFRESH_COOKIE_MAX_AGE)
        self.assertEqual(cookie["samesite"], "Strict")
        self.assertTrue(cookie["httponly"])
        self.assertEqual(bool(cookie["secure"]), settings.JWT_REFRESH_COOKIE_SECURE)

    def test_refresh_restores_access_token_and_logout_deletes_cookie(self):
        self.login()
        old_value = self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME].value

        csrf_response = self.client.get(reverse("csrf-cookie"))
        csrf_token = csrf_response.cookies["csrftoken"].value
        self.client.cookies["csrftoken"] = csrf_token
        response = self.client.post(reverse("token_refresh"), HTTP_X_CSRFTOKEN=csrf_token)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"access"})
        new_value = self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        self.assertEqual(new_value, old_value)
        response = self.client.post(reverse("token_logout"), HTTP_X_CSRFTOKEN=csrf_token)

        self.assertEqual(response.status_code, 204)
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertEqual(cookie["max-age"], 0)
        self.assertEqual(cookie["path"], "/api/auth/")
