# Python debugging example
import sys, logging
from rainbow_logging_handler import RainbowLoggingHandler


logger = logging.getLogger(__name__)


def my_func(a, b):
    return a + b

if __name__ == "__main__":
    my_func(1, "2")