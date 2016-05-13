"""Sending out HTML and plain text email."""
from email.header import Header
from email.utils import formataddr

from pyramid.renderers import render

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import premailer


def send_templated_mail(request, recipients, template, context, sender=None):
    """Send out templatized HTML and plain text emails.

    Each HTML email should have a plain text fallback. Premailer package is used to convert any CSS styles in HTML email messages to inline, so that email clients display them.

    The email is assembled from three different templates:

    * Read subject from a subject specific template $template.subject.txt

    * Generate HTML email from HTML template, $template.body.html

    * Generate plain text email from HTML template, $template.body.txt

    Make sure you have configured your template engine (Jinja 2) to read TXT templates beside HTML.

    :param request: HTTP request, passed to the template engine. Request configuration is used to get hold of the configured mailer.

    :param recipients: List of recipient emails

    :param template: Template filename base string for template tripled (subject, HTML body, plain text body). For example ``email/my_message`` would map to templates ``email/my_message.subject.txt``, ``email/my_message.body.txt``, ``email/my_message.body.html``

    :param context: Template context variables as a dict

    :param sender: Override the sender email - if not specific use the default set in the config as ``mail.default_sender``
    """

    assert recipients
    assert len(recipients) > 0
    assert type(recipients) != str, "Please give a list of recipients, not a string"

    for r in recipients:
        assert r, "Received empty recipient when sending out email {}".format(template)

    subject = render(template + ".subject.txt", context, request=request)
    subject = subject.strip()

    html_body = render(template + ".body.html", context, request=request)
    text_body = render(template + ".body.txt", context, request=request)

    if not sender:
        sender = request.registry.settings["mail.default_sender"]

        # Add enveloped From:
        sender_name =  request.registry.settings.get("mail.default_sender_name")
        if sender_name:
            sender = formataddr((str(Header(sender_name, 'utf-8')), sender))


    # Inline CSS styles
    html_body = premailer.transform(html_body)

    message = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)

    mailer = get_mailer(request)
    mailer.send(message)
