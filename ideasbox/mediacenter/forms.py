from django import forms

from .models import Document
from .utils import guess_kind_from_content_type


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = '__all__'

    def save(self, commit=True):
        document = super(DocumentForm, self).save(commit=False)
        original = self.cleaned_data['original']
        # When editing a form, original is a FileField, not an UploadedFile,
        # so we don't have content_type.
        content_type = getattr(original, 'content_type', None)
        kind = guess_kind_from_content_type(content_type)
        if kind:
            document.kind = kind
        document.save()
        self.save_m2m()
        return document
