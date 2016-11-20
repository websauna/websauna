from websauna.system.http import Request


class TaskFinished:
    """This task is fired when a Celery task finishes regardless if the task failed or not.

    Intended to be used to clean up thread current context sensitive data.

    This is called before ``request._process_finished_callbacks()`` is called. This is **not** called when tasks are executed eagerly.
    """

    def __init__(self, request: Request, task: "websauna.system.core.task.tasks.WebsaunaTask"):
        self.request = request
        self.task = task
