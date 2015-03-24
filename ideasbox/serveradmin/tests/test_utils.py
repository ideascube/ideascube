import pytest

from ..utils import call_service


@pytest.mark.parametrize("name,action,stdout,stderr,error,status,returncode", [
    ("apache2", "status", "apache2 is running", None, None, True, 0),
    ("apache2", "status", "apache2 is not running", None, None, False, 3),
    ("apache2", "status", None, "apache2: unrecognized service",
     "apache2: unrecognized service", False, 1),
])
def test_call_service(monkeypatch, name, action, stdout, stderr, error,
                      status, returncode):
    class Mock(object):
        def __init__(self, *args, **kwargs):
            self.returncode = returncode

        def communicate(self):
            return stdout, stderr

    monkeypatch.setattr("subprocess.Popen", Mock)
    resp = call_service({"name": name, "action": action})
    assert resp.get("error") == error
    assert resp.get("status") == status
