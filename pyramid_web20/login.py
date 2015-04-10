"""User log in and sign up related logic."""

from hem.db import get_session

from horus import views as horus_views
from horus.interfaces import IActivationClass

from .mail import send_templated_mail


def create_activation(request, user):
    db = get_session(request)
    Activation = request.registry.getUtility(IActivationClass)
    activation = Activation()

    db.add(activation)
    user.activation = activation

    db.flush()

    # TODO Create a hook for the app to give us body and subject!
    # TODO We don't need pystache just for this!
    context = {
        'link': request.route_url('activate', user_id=user.id,
                                  code=user.activation.code)
    }

    send_templated_mail(request, [user.email], "login/email/activate", context)


def activate_monkey_patch():
    # Monkey patch horus to do nice email outs
    horus_views.create_activation = create_activation


def includeme():
    config.registry.registerUtility(SubmitForm, form)