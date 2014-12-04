import pytest

from django.core.urlresolvers import reverse


pytestmark = pytest.mark.django_db


def test_services_page(app):
    assert app.get('/server/services/', status=200)


def test_services_page_in_GET_mode(app):
    assert app.get(reverse('server:services'), status=200)
