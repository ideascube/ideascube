from django.core.management import call_command

import pytest


def test_no_command(capsys):
    with pytest.raises(SystemExit):
        call_command('config')

    out, err = capsys.readouterr()
    assert out.strip().startswith('usage: ')
    assert err.strip() == ''
