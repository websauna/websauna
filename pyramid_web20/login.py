"""User log in and sign up related logic."""

from horus import views as horus_views

def create_activation(request, user):
    db = get_session(request)
    Activation = request.registry.getUtility(IActivationClass)
    activation = Activation()

    db.add(activation)
    user.activation = activation

    db.flush()

    # TODO Create a hook for the app to give us body and subject!
    # TODO We don't need pystache just for this!
    body = pystache.render(
        _("Please validate your email and activate your account by visiting:\n"
            "{{ link }}"),
        {
            'link': request.route_url('activate', user_id=user.id,
                                      code=user.activation.code)
        }
    )
    subject = _("Please activate your account!")

    message = Message(subject=subject, recipients=[user.email], body=body)
    mailer = get_mailer(request)
    mailer.send(message)

# Monkey patch horus to do nice email outs
horus_views.create_activation = create_activation