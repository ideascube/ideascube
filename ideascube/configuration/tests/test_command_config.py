from django.core.management import call_command
from django.core.management.base import CommandError

import pytest


def test_no_command(capsys):
    with pytest.raises(SystemExit):
        call_command('config')

    out, err = capsys.readouterr()
    assert out.strip().startswith('usage: ')
    assert err.strip() == ''


def test_list_namespaces(capsys, monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'namespace2': {'key2': {}}, 'namespace1': {}})

    call_command('config', 'list')

    out, err = capsys.readouterr()
    assert out.strip().split('\n') == ['namespace1', 'namespace2']
    assert err.strip() == ''


def test_list_no_namespaces(capsys, monkeypatch):
    monkeypatch.setattr('ideascube.configuration.registry.REGISTRY', {})

    call_command('config', 'list')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_list_keys(capsys, monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'namespace1': {'key1': {}, 'key2': {}}})

    call_command('config', 'list', 'namespace1')

    out, err = capsys.readouterr()
    assert out.strip().split('\n') == ['namespace1 key1', 'namespace1 key2']
    assert err.strip() == ''


def test_list_no_keys(capsys, monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY', {'namespace1': {}})

    call_command('config', 'list', 'namespace1')

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip() == ''


def test_list_keys_invalid_namespace(capsys, monkeypatch):
    monkeypatch.setattr('ideascube.configuration.registry.REGISTRY', {})

    with pytest.raises(CommandError) as exc_info:
        call_command('config', 'list', 'namespace1')

    assert (
        'Unknown configuration namespace: "namespace1"') in str(exc_info.value)
