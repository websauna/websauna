from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import premailer


class StdoutMailer(object):
    """Print all outgoing email to console.

    Used by the development server.
    """

    def __init__(self):
        # For testing purposes
        self.send_count = 0

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging
        """
        print(str(message.to_message()))
        self.send_count += 1

    send = _send
    send_immediately = _send
    send_to_queue = _send
    send_sendmail = _send
    send_immediately_sendmail = _send


def send_templated_mail(request, recipients, template, context, sender=None):
    """Send out templatized HTML and plain text emails.

    The email is assembled from three different templates:

    * Read subject from a subject specific template $template.subject.txt

    * Generate HTML email from HTML template, $template.body.html

    * Generate plain text email from HTML template, $template.body.txt

    :param request: HTTP request, passed to the template engine. Request configuration is used to get hold of the configured mailer.

    :param recipients: List of recipient emails

    :param template: Template filename base string for template tripled (subject, HTML body, plain text body). For example ``email/my_message`` would map to templates ``email/my_message.subject.txt``, ``email/my_message.body.txt``, ``email/my_message.body.html``

    :param context: Template context variables as a dict

    :param sender: Override the sender email - if not specific use the default set in the config as ``mail.default_sender``
    """

    assert recipients
    assert len(recipients) > 0
    assert type(recipients) != str, "Please give a list of recipients, not a string"

    subject = render(template + ".subject.txt", context, request=request)
    subject = subject.strip()

    html_body = render(template + ".body.html", context, request=request)
    text_body = render(template + ".body.txt", context, request=request)

    if not sender:
        sender = request.registry.settings["mail.default_sender"]

    # Inline CSS styles
    html_body = premailer.transform(html_body)

    message = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)

    mailer = get_mailer(request)
    mailer.send(message)
