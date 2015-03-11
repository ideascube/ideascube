from django import forms

from .models import Content


class ContentForm(forms.ModelForm):

    class Meta:
        model = Content
        widgets = {
            # We need a normalized date string for JS datepicker, so we take
            # control over the format to bypass L10N.
            "published_at": forms.DateInput(format='%Y-%m-%d')
        }
        fields = "__all__"
