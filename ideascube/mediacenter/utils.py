import mimetypes


def guess_kind_from_filename(filepath):
    """Return a document kind (image, audio...) guessed from a filename. If
    no kind can be guessed, returns None."""
    if filepath:
        content_type, _ = mimetypes.guess_type(filepath)
        return guess_kind_from_content_type(content_type)


def guess_kind_from_content_type(content_type):
    """Return a document kind (image, audio...) guessed from a content_type. If
    no kind can be guessed, returns None."""
    lookups = ['image', 'video', 'audio', 'text', 'pdf']
    if content_type:
        for lookup in lookups:
            if lookup in content_type:
                return lookup
