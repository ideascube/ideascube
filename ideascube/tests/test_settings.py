import importlib

import pytest


def test_all_settings(request):
    confdir = request.fspath.dirpath().dirpath().join('conf')
    assert confdir.check(dir=True)
    count = 0

    for path in confdir.listdir():
        if path.ext != '.py':
            continue

        count += 1
        module = path.purebasename
        module = '.conf.%s' % module

        try:
            settings = importlib.import_module(module, package="ideascube")

        except Exception as e:
            print(path)
            print(module)
            pytest.fail(str(e))

        assert isinstance(getattr(settings, 'IDEASCUBE_NAME', ''), str)

    # Make sure we have actually tested some files.
    assert count
