from datetime import datetime, timezone

import freezegun

import pytest

from ideascube.configuration.models import Configuration


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('value', [
    pytest.param(True, id='boolean'),
    pytest.param(42, id='int'),
    pytest.param(None, id='none'),
    pytest.param('A string', id='string'),
    pytest.param([1, '2'], id='list'),
])
def test_configuration(value, user):
    fakenow = datetime.now(tz=timezone.utc)
    assert Configuration.objects.count() == 0

    with freezegun.freeze_time(fakenow):
        Configuration(
            namespace='tests', key='setting1', value=value, actor=user).save()

    assert Configuration.objects.count() == 1

    configuration = Configuration.objects.first()
    assert configuration.namespace == 'tests'
    assert configuration.key == 'setting1'
    assert configuration.value == value
    assert configuration.actor == user
    assert configuration.date == fakenow
    assert str(configuration) == 'tests.setting1=%r' % value
