# XXX: Not we use what horus provides internally
from horus.lib import FlashMessage


def add(request, msg, kind="info"):
    """"""

    # Don't postpone problems through serialization
    assert type(msg) == str
    assert kind in FlashMessage.KINDS
    FlashMessage(request, msg, kind=kind)