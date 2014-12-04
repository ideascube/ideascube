import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse


pytestmark = pytest.mark.django_db
user_model = get_user_model()


def test_services_page(app):
    assert app.get('/server/services/', status=200)


def test_services_page_in_GET_mode(app):
    assert app.get(reverse('server:services'), status=200)
