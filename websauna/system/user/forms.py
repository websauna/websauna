from deform import Form
from deform import Button


class DefaultUserForm(Form):
    """Form implementation used for all user forms.

    Comes with one submit button.
    """

    def __init__(self, *args, **kwargs):
        if not kwargs.get('buttons'):
            kwargs['buttons'] = ('submit',)
        super().__init__(*args, **kwargs)



class DefaultLoginForm(Form):
    """Form used by default Login by email screen."""

    def __init__(self, *args, **kwargs):
        if not kwargs.get('buttons'):
            login_button = Button(name="login_email", title="Login with email", css_class="btn-lg btn-block")
            kwargs['buttons'] = (login_button,)
        super().__init__(*args, **kwargs)
