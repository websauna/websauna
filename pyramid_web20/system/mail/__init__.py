from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Attachment
from pyramid_mailer.message import Message

import premailer


class StdoutMailer(object):
    """Print all outgoing email to console.

    Used by the development server.
    """
    def __init__(self):
        pass

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging
        """
        print(str(message.to_message()))

    send = _send
    send_immediately = _send
    send_to_queue = _send
    send_sendmail = _send
    send_immediately_sendmail = _send


def send_templated_mail(request, recipients, template, context, sender=None):
    """Helper utility to send out HTML/plain text emails.

    Plain text email is generated based on HTML email.

    * Read subject from a subject specific template

    * Convert HTML output to plain text for fallback

    :param template: Template filename base for template tripled (subject, HTML body, plain text body)

    :param context: Template context variables
    """

    # TODO: move request usage out from this function and make sure we can call this asynchronously

    assert recipients
    assert len(recipients) > 0

    subject = render(template + ".subject.txt", context, request=request)
    subject = subject.strip()

    html_body = render(template + ".body.html", context, request=request)
    text_body = render(template + ".body.txt", context, request=request)

    if not sender:
        sender = request.registry.settings["mail.default_sender"]

    # Inline CSS styles
    html_body = premailer.transform(html_body)

    text_body = Attachment(data=text_body, transfer_encoding="quoted-printable")
    html_body = Attachment(data=html_body, transfer_encoding="quoted-printable")

    message = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)

    mailer = get_mailer(request)
    mailer.send(message)
