from pyramid.request import Request


class FlashMessage(object):
    """Adoption of Horus flash message.

    Provisional internal API, subject to change.
    """

    # High traffic sites might have plenty of these objects, so optimize memory usage here a bit
    __slots__ = ('kind', 'plain', 'rich', 'msg_id', 'extra')

    KINDS = set(['error', 'warning', 'info', 'success'])

    def __getstate__(self):
        '''Because we are using __slots__, pickling needs this method.'''
        return {'kind': self.kind, 'plain': self.plain, 'rich': self.rich, 'msg_id': self.msg_id, 'extra': self.extra}

    def __setstate__(self, state):
        self.kind = state.get('kind')
        self.plain = state.get('plain')
        self.rich = state.get('rich')
        self.msg_id = state.get('msg_id')
        self.extra = state.get('extra')

    def __init__(self, plain=None, rich=None, kind='warning',
                 allow_duplicate=False, msg_id=None, extra=None):
        assert (plain and not rich) or (rich and not plain)
        assert kind in self.KINDS, "Unknown kind of alert: \"{}\". " \
            "Possible kinds are {}".format(kind, self.KINDS)

        # TODO: clean up rich and plain stuff
        self.kind = kind
        self.rich = rich
        self.plain = plain
        self.msg_id = msg_id
        self.extra = extra

    def __repr__(self):
        return 'FlashMessage("{}")'.format(self.plain)

    def __unicode__(self):
        return self.rich or self.plain

    def get_id(self):
        """Allows session storage to know if this message has been already added."""
        return any((self.msg_id, self.rich, self.plain,))

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)



def add(request: Request, msg: str, kind: str="info", msg_id :str=None, extra: dict=None, html=False, allow_duplicates=False):
    """Add a message which is shown to the user on the next page load.

    This is so called Flash message. The message is stored in the session. On the next page load, the HTML templates and framework must read all pending messages from the session store and display them to the user. Usually this is a notification rendered at the top of the page.

    Duplicate messages are discarded.

    Messages are stored in the session queue, keyed by the message kind.

    :param msg: Message as a string
    :param kind: One of 'error', 'warning', 'info', 'success'. Defaults to 'info'
    :param msg_id: CSS id set on the alert box. Useful for functional testing.
    :param html: The message is HTML
    :param extra: Dictionary of application specific extra parameters or None. The content must be pickable.
    :param allow_duplicates: Allow duplicate messages
    """

    # Don't postpone problems through serialization if the user gives non-str object accidentally
    assert type(msg) == str

    if html:
        msg = FlashMessage(rich=msg, kind=kind, msg_id=msg_id, extra=extra)
    else:
        msg = FlashMessage(plain=msg, kind=kind, msg_id=msg_id, extra=extra)

    request.session.flash(msg, queue=kind, allow_duplicate=allow_duplicates)


def clear(request: Request, kinds=("info", "error", "warning", "success")):
    """Clear all messages from the flash message queue."""

    for kind in kinds:
        request.session.pop_flash(queue=kind)