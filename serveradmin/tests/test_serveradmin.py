import pytest

from django.core.urlresolvers import reverse
from serveradmin.utils import call_service


pytestmark = pytest.mark.django_db


def test_services_page_in_GET_mode(app):
    assert app.get(reverse('server:services'), status=200)


@pytest.mark.parametrize("name,action,stdout,stderr,error,status", [
    ('apache2', 'status', "apache2 is running", None, None, True),
    ('apache2', 'status', "apache2 is not running", None, None, False),
    ('apache2', 'status', None, "apache2: unrecognized service",
     "apache2: unrecognized service", None),
])
def test_call_service(monkeypatch, name, action, stdout, stderr, error,
                      status):
    class Mock(object):
        def __init__(self, *args, **kwargs):
            pass

        def communicate(self):
            return stdout, stderr

    monkeypatch.setattr("subprocess.Popen", Mock)
    resp = call_service({'name': name, 'action': action})
    assert resp.get('error') == error
    assert resp.get('status') == status
