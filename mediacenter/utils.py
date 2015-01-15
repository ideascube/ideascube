import mimetypes


def guess_kind(filepath):
    """Return a document kind (image, audio...) guessed from a filename. If
    no kind can be guessed, returns None."""
    lookups = ['image', 'video', 'audio', 'text', 'pdf']
    if filepath:
        kind, encoding = mimetypes.guess_type(filepath)
        if not kind:
            return
        for lookup in lookups:
            if lookup in kind:
                return lookup
