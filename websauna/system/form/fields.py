import colander


class UUID(colander.String):
    """UUID field for Colander.

    See also :py:class`websauna.system.form.widgets.FriendlyUUIDWidget`.
    """

    def serialize(self, node, appstruct):
        # Assume widgets can handle raw UUID object
        return appstruct
