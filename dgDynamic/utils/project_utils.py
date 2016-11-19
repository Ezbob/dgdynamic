import logging
import os
import shutil
import time
from ..config.settings import config
from typing import *
from .logger import logging_handler


def log_it(function):
    """
    Use this function as decorator, to enable logging for a function
    :param function: the function that has been decorated
    :return: the wrapper that decorates the function
    """
    name = ".".join([function.__module__, function.__name__])
    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)

    def debug_wrapper(*args, **kwargs):
        logger.info("Now entering function {} with arguments {} and \
keyword arguments {}".format(function.__name__, args, kwargs))
        started = time.time()
        output = function(*args, **kwargs)
        ended = time.time()
        logger.info("Leaving function output: {}".format(output))
        logger.info("Execution time was {} secs".format(ended - started))
        debug_wrapper.__name__ = function.__name__
        return output
    return debug_wrapper


class LogMixin:
    """
    Handy code for injecting a logger instance in any class.
    """
    @property
    def logger(self):
        name = ".".join([self.__class__.__module__, self.__class__.__name__])
        log_machine = logging.getLogger(name)
        log_machine.addHandler(logging_handler)
        return log_machine





def make_directory(path, pre_delete=False):
    """
    This function just provides a mkdir functionality that can delete the contents of a
    folder if so needed.
    :param path: path the new directory
    :param pre_delete: shall it destroy the already existing folder?
    :return: None
    """
    if os.path.exists(path) and pre_delete is True:
            shutil.rmtree(path)
            os.mkdir(path)
    elif not os.path.exists(path):
        os.mkdir(path)


class ProjectTypeHints:
    Real = Union[float, int]
    Reals = List[Real]
    Numbers = Union[Reals, Real]
    Countable_Sequence = Union[List[Any], Tuple[Any, ...], Set[Any]]
    ODE_Function = Callable[[Numbers, Numbers], Numbers]
