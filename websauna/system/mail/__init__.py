"""Sending out HTML and plain text email."""
from email._policybase import Compat32
from email.header import Header
from email.utils import formataddr

from pyramid.renderers import render
from pyramid.settings import asbool

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import premailer

from websauna.system.http import Request
from websauna.compat.typing import Iterable


def send_templated_mail(request: Request, recipients: Iterable, template: str, context: dict, sender=None, immediate=None):
    """Send out templatized HTML and plain text emails.

    Each HTML email should have a plain text fallback. Premailer package is used to convert any CSS styles in HTML email messages to inline, so that email clients display them.

    The email is assembled from three different templates:

    * Read subject from a subject specific template $template.subject.txt

    * Generate HTML email from HTML template, $template.body.html

    * Generate plain text email from HTML template, $template.body.txt

    Make sure you have configured your template engine (Jinja 2) to read TXT templates beside HTML.

    Example to send email with a custom From header, using ``myapp/email/welcome.body.html`` as the body template:

    .. code-block:: python

        from email.header import Header
        from email.utils import formataddr

        # I never receive any letters
        to_email = "mikko@example.com"

        # Build a proper From header with both name and email,
        # otherwise the sender defaults to the site INI settings
        sender = formataddr((str(Header(order.get_sender_name(), 'utf-8')), order.get_from_email()))

        # Pass some variables to subject and body templates
        context = dict(greeting="Welcome human!", tag_line="We come in peace")

        send_templated_mail(self.request, [to_email], "myapp/email/welcome", context=context, sender=sender)


    :param request: HTTP request, passed to the template engine. Request configuration is used to get hold of the configured mailer.

    :param recipients: List of recipient emails

    :param template: Template filename base string for template tripled (subject, HTML body, plain text body). For example ``email/my_message`` would map to templates ``email/my_message.subject.txt``, ``email/my_message.body.txt``, ``email/my_message.body.html``

    :param context: Template context variables as a dict

    :param sender: Override the sender email - if not specific use the default set in the config as ``mail.default_sender``

    :param immediate: Set True to send to the email immediately and do not wait the transaction to commit. This is very useful for debugging outgoing email issues in an interactive traceback inspector. If this is ``None`` then use setting ``mail.immediate`` that defaults to ``False``.
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
    message.validate()

    mailer = get_mailer(request)

    if immediate is None:
        immediate = asbool(request.registry.settings.get("mail.immediate", False))

    if immediate:
        mailer.send_immediately(message)
    else:
        mailer.send(message)
