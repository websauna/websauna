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
