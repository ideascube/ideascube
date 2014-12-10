from django import forms

from .models import BookSpecimen, Book


class BookSpecimenForm(forms.ModelForm):

    class Meta:
        model = BookSpecimen
        widgets = {'book': forms.HiddenInput}
        fields = '__all__'


class BookForm(forms.ModelForm):

    def clean_isbn(self):
        # Make sure empty values are mapped to None, not empty string.
        return self.cleaned_data['isbn'] or None

    class Meta:
        model = Book
        fields = '__all__'
