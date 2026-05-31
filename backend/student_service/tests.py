from django.test import Client
from django.urls import reverse


def test_health_endpoint_returns_ok():
    response = Client().get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_jwt_token_urls_are_registered():
    assert reverse("token_obtain_pair") == "/api/auth/token/"
    assert reverse("token_refresh") == "/api/auth/token/refresh/"
