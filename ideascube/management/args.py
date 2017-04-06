import argparse
import datetime


def date_argument(arg):
    try:
        dt = datetime.datetime.strptime(arg, '%Y-%m-%d')

    except ValueError:
        msg = 'Not a valid date: "{}"'.format(arg)
        raise argparse.ArgumentTypeError(msg)

    return dt.replace(tzinfo=datetime.timezone.utc)
