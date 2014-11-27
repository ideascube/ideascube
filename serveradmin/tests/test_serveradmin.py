import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse


pytestmark = pytest.mark.django_db
user_model = get_user_model()


def test_services_page(client):
    response = client.get('/server/services/')
    assert response.status_code == 200


def test_services_page_in_GET_mode(client):
    response = client.get(reverse('server:services'))
    assert response.status_code == 200
