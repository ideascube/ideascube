from django import forms
from django.contrib.auth import get_user_model


class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.iteritems():
            if isinstance(field, forms.DateField):
                # Force date format on load, so date picker doesn't mess it up
                # because of i10n.
                field.widget = forms.DateInput(format='%Y-%m-%d')

    class Meta:
        model = get_user_model()
        exclude = ['password', 'last_login', 'is_staff']
