from pyramid_mailer.message import Attachment
from pyramid_mailer.message import Message


class StdoutMailer(object):
    """Print all outgoing email to console.

    """
    def __init__(self):
        pass

    def _message_args(self, message):

        message.sender = message.sender or self.default_sender
        # convert Lamson message to Python email package msessage
        msg = message.to_message()
        return (message.sender, message.send_to, msg)

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging
        """
        print(str(message.to_message()))

    send = _send
    send_immediately = _send
    send_to_queue = _send
    send_sendmail = _send
    send_immediately_sendmail = _send


def email_out(recipients, template, template_context):
    """Helper utility to send out HTML/plain text emails.

    Plain text email is generated based on HTML email.

    * Read subject from a subject specific template

    * Convert HTML output to plain text for fallback

    :param template: Template filename base for template tripled (subject, HTML body, plain text body)
    """

    body = Attachment(data="hello, arthur",
                      transfer_encoding="quoted-printable")

    html = Attachment(data="<p>hello, arthur</p>",
                      transfer_encoding="quoted-printable")

    message = Message(subject=subject, body=body, html=html)