import io
import sys

from django.conf import locale


class classproperty(property):
    """
    Use it to decorate a classmethod to make it a "class property".
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class TextIOWrapper(io.TextIOWrapper):
    def __init__(self, buffer, encoding=None, **kwargs):
        if encoding is None:
            try:
                buffer.read().decode('utf-8')

            except UnicodeDecodeError:
                # FIXME: If this ever causes problems, we can go with cchardet
                encoding = 'latin-1'

            else:
                encoding = 'utf-8'

            buffer.seek(0)

        super().__init__(buffer, encoding=encoding, **kwargs)


def get_all_languages():
    languages = []

    for language, lang_data in locale.LANG_INFO.items():
        try:
            languages.append(
                (language, lang_data['name_local'].capitalize())
            )

        except KeyError:
            # That language doesn't have a local name, only a fallback
            continue

    return sorted(languages)


# We do not use functool.partial cause we want to mock stderr for unittest
# If we use partial we keep a ref to the original sys.stderr and output is not
# captured.
def printerr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    kwargs['flush'] = True
    return print(*args, **kwargs)


def to_unicode(text):
    """Do its best to return an unicode string."""
    text = text or ''
    if isinstance(text, str):
        return text
    else:
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            text = text.decode('latin-1')
        return text
