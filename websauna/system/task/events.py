from websauna.system.http import Request


class TaskFinished:
    """Posted always when a Celery tasks finished regarless if it failed or not.

    Can be used to clean up thread current context sensitivedata.

    This is called before ``request._process_finished_callbacks()`` is called.
    """

    def __init__(self, request: Request, task: "websauna.system.core.task.tasks.WebsaunaTask"):
        self.request = request
        self.task = task
