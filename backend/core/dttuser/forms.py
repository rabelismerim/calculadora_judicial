from django.forms import ModelForm
from django.contrib.auth.forms import UsernameField

from .models import User

class UserCreationForm(ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True