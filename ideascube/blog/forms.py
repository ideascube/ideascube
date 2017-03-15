from django import forms

from ideascube.widgets import LangSelect, RichTextEntry

from .models import Content


class ContentForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Content
        widgets = {
            # We need a normalized date string for JS datepicker, so we take
            # control over the format to bypass L10N.
            "published_at": forms.DateInput(format='%Y-%m-%d'),
            "lang": LangSelect,
            "text": RichTextEntry(with_media=True)
        }
        fields = "__all__"

    def save(self, commit=True):
        content = super().save()
        content.save()  # Index m2m.
        return content
