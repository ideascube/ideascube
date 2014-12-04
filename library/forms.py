from django import forms

from .models import BookSpecimen


class BookSpecimenForm(forms.ModelForm):

    class Meta:
        model = BookSpecimen
        widgets = {'book': forms.HiddenInput}
