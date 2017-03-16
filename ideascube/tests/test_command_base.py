import pytest


def test_no_subcommand(capsys):
    from ideascube.management.base import BaseCommandWithSubcommands

    cmd = BaseCommandWithSubcommands()

    with pytest.raises(SystemExit):
        cmd.run_from_argv(['', 'dummy'])

    out, err = capsys.readouterr()
    assert out.strip().startswith('usage: ')
    assert err.strip() == ''
