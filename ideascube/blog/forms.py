from django import forms
from django.utils.translation import get_language

from ideascube.widgets import LangSelect, RichTextEntry

from .models import Content


class ContentForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Content
        widgets = {
            "author": forms.HiddenInput,
            # We need a normalized date string for JS datepicker, so we take
            # control over the format to bypass L10N.
            "published_at": forms.DateInput(format='%Y-%m-%d'),
            "lang": LangSelect,
            "summary": RichTextEntry,
            "text": RichTextEntry(with_media=True)
        }
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['lang'] = get_language()

    def save(self, commit=True):
        content = super().save()
        content.save()  # Index m2m.
        return content
