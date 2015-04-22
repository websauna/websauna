Sending out test mail:

    from pyramid_mailer import get_mailer
    from pyramid_mailer.message import Message

    sender = request.registry.settings["mail.default_sender"]

    message = Message(subject="pyramid_mailer test", sender="no-reply@redinnovation.com", recipients=["mikko@redinnovation.com"], body="yyy")

    mailer = get_mailer(request)
    mailer.send_immediately_sendmail(message)

