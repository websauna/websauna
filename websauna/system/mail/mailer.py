from pyramid_mailer.mailer import DummyMailer


class StdoutMailer:
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


class NullMailer:
    """Ignore all otugoing mail and only increase send count.

    Functional testing email backend.
    """

    def __init__(self):
        # For testing purposes
        self.send_count = 0

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging
        """
        self.send_count += 1

    send = _send
    send_immediately = _send
    send_to_queue = _send
    send_sendmail = _send
    send_immediately_sendmail = _send


class ThreadFriendlyDummyMailer(DummyMailer):
    """Multi-thread aware mailing test backend.

    We store outbox messages in class globals. If a web server or another thread sends out a message this allows us to access the message in a test thread.
    """

    outbox = []
    queue = []

    def __init__(self):
        # Override DummyMailer self init here
        pass

    @classmethod
    def reset(cls):
        ThreadFriendlyDummyMailer.outbox = []
        ThreadFriendlyDummyMailer.queue = []

    def _send(self, message, fail_silently=False):
        """Save message to a file for debugging"""
        self.output.append(message)
        self.send_count += 1
