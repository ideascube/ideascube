import io
import sys
import os
import re

from django.conf import locale
from hashlib import sha256


class classproperty(property):
    """
    Use it to decorate a classmethod to make it a "class property".
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class TextIOWrapper(io.TextIOWrapper):
    def __init__(self, buffer, encoding=None, **kwargs):
        if encoding is None:
            content = buffer.read()

            try:
                content.decode('utf-8')

            except UnicodeDecodeError:
                # FIXME: If this ever causes problems, we can go with cchardet
                encoding = 'latin-1'

            else:
                encoding = 'utf-8'

            buffer = io.BytesIO(content)

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

def get_file_sha256(path):
    sha = sha256()

    with open(path, 'rb') as f:
        while True:
            data = f.read(8388608)

            if not data:
                break

            sha.update(data)

    return sha.hexdigest()

def get_file_size(path):
    return os.stat(path).st_size

def tag_splitter(tag_string):
    tags = set(t.strip() for t in re.split(r'[;,]+', tag_string) if t.strip())
    return list(tags)
