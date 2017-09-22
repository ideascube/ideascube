import os.path
import mimetypes


def guess_kind_from_filename(filepath):
    """Return a document kind (image, audio...) guessed from a filename. If
    no kind can be guessed, returns None."""
    if filepath:
        content_type, _ = mimetypes.guess_type(filepath)
        kind = guess_kind_from_content_type(content_type)
        if kind:
            return kind
        return guess_kind_from_extension(filepath)


def guess_kind_from_extension(filepath):
    """Return a document kind (image, audio...) guessed from a filename.
    Guess is based on the extension. If no kind can be guessed, returns None."""
    ext_to_kind = {
        '.epub': 'epub',
        '.mobi': 'mobi',
        '.exe': 'app',
    }
    extension = os.path.splitext(filepath)[1].lower()
    return ext_to_kind.get(extension)


def guess_kind_from_content_type(content_type):
    """Return a document kind (image, audio...) guessed from a content_type. If
    no kind can be guessed, returns None."""
    lookups = ['image', 'video', 'audio', 'text', 'pdf', 'epub', 'mobi']
    if content_type:
        for lookup in lookups:
            if lookup in content_type:
                return lookup
