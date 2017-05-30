import io
import os
import re
import shutil
import sys
import urllib.error, urllib.parse

from django.conf import locale
from hashlib import sha256
from resumable import (
    DownloadCheck, DownloadError,
    urlretrieve as resumable_urlretrieve,
)


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


class URLRetrieveError(urllib.error.URLError):
    def __str__(self):
        return '{self.filename}: {self.reason}'.format(self=self)


def urlretrieve(url, dest_path, sha256sum=None, reporthook=None):
    parsed_url = urllib.parse.urlparse(url)

    if parsed_url.scheme not in ('file', 'http', 'https'):
        raise ValueError('Unsupported URL scheme: {url}'.format(url=url))

    if parsed_url.scheme == 'file':
        shutil.copyfile(parsed_url.path, dest_path)

        if sha256sum is not None:
            sha = get_file_sha256(dest_path)

            if sha != sha256sum:
                rm(dest_path)
                raise URLRetrieveError(
                    'Invalid checksum: expected {sha256sum}, got {sha}'
                    .format(sha256sum=sha256sum, sha=sha))

    else:
        try:
            resumable_urlretrieve(
                url, dest_path, sha256sum=sha256sum, reporthook=reporthook)

        except DownloadError as e:
            if e.args[0] is DownloadCheck.checksum_mismatch:
                # We don't get the computed sha unfortunately :(
                msg = 'Invalid checksum: expected {sha256sum}'.format(
                    sha256sum=sha256sum)

            else:
                msg = 'Download error: {e}'.format(e=e)

            rm(dest_path)
            raise URLRetrieveError(msg, filename=url)


def rm(path):
    try:
        os.unlink(path)

    except IsADirectoryError:
        shutil.rmtree(path)

    except FileNotFoundError:
        # That's fine
        pass


def sanitize_tag_name(tag_name):
    tag_name = tag_name.strip(';:.,?!+-@+-/* \t')
    tag_name = tag_name.lower()
    return tag_name


def tag_splitter(tag_string):
    tags = set(sanitize_tag_name(t) for t in re.split(r'[;,]+', tag_string))
    return list(tag for tag in tags if tag)
