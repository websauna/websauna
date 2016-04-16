from deform import Form


class DefaultUserForm(Form):
    """Form implementation used for all user forms.

    Comes with one submit button.
    """

    def __init__(self, *args, **kwargs):
        if not kwargs.get('buttons'):
            kwargs['buttons'] = ('submit',)
        super().__init__(*args, **kwargs)

