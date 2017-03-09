import argparse
from datetime import datetime, timezone

import pytest


@pytest.mark.parametrize(
    'input', [
        '2017-03-09', '2017-03-9', '2017-3-09', '2017-3-9',
    ])
def test_date_argument(input):
    from ideascube.management.args import date_argument

    expected = datetime(2017, 3, 9, tzinfo=timezone.utc)
    assert date_argument(input) == expected


@pytest.mark.parametrize(
    'bad_input', [
        '2017-31-12', '31-12-2017', '12-31-2017', '2017 12 31', '2017 31 12',
        '20171231', '20173112',
    ])
def test_invalid_date_argument(bad_input):
    from ideascube.management.args import date_argument

    with pytest.raises(argparse.ArgumentTypeError) as e:
        date_argument(bad_input)

    assert str(e.value) == 'Not a valid date: "{}"'.format(bad_input)
