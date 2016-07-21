from django import forms
from django.conf import settings

from ideascube.fields import LangSelect

from .models import Document
from .utils import guess_kind_from_content_type

import os


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = '__all__'
        widgets = {
            'lang': LangSelect,
        }

    def save(self, commit=True):
        document = super().save(commit=False)
        original = self.cleaned_data['original']
        # When editing a form, original is a FileField, not an UploadedFile,
        # so we don't have content_type.
        content_type = getattr(original, 'content_type', None)
        kind = guess_kind_from_content_type(content_type)
        if kind:
            document.kind = kind
        if commit:
            if not document.id:
                # m2m need the document to have an id.
                document.save()
            self.save_m2m()
            document.save()  # Search index needs m2m to be saved.
        return document


class PackagedDocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        exclude = ['original', 'preview']

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original'] = forms.FilePathField(path=path)
        self.fields['preview'] = forms.FilePathField(path=path, required=False)

    def save(self, commit=True):
        document = super(PackagedDocumentForm, self).save(commit=False)
        original = self.cleaned_data['original']
        original = os.path.relpath(original, settings.MEDIA_ROOT)
        document.original = original

        preview = self.cleaned_data.get('preview', None)
        if preview:
            preview = os.path.relpath(preview, settings.MEDIA_ROOT)
            document.preview = preview

        if commit:
            if not document.id:
                document.save()
            self.save_m2m()
            document.save()
        return document
