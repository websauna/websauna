import os
import pytest


@pytest.fixture(scope='module')
def task_ini_file():
    return os.path.join(os.path.dirname(__file__), 'task-test.ini')
