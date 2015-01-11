import mimetypes


def guess_type(filepath):
    lookups = ['image', 'video', 'audio', 'text', 'pdf']
    if filepath:
        _type, encoding = mimetypes.guess_type(filepath)
        if not _type:
            return
        for lookup in lookups:
            if lookup in _type:
                return lookup
