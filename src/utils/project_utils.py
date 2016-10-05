import logging
import config
import os
import shutil
from typing import *
logging_handler = None


def log(function):
    """
    Use this function as decorator
    :param function: the function that has been decorated
    :return: the wrapper that decorates the function
    """
    global logging_handler
    name = ".".join([function.__module__, function.__name__])
    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)

    def debug_wrapper(*args, **kwargs):
        logger.info("Now entering function {} with arguments {} and\
keyword arguments {}".format(function.__name__(), args, kwargs))
        function(args, kwargs, logger=function)
        logger.info("Leaving function {}".format(args))
        debug_wrapper.__name__ = function.__name__
    return debug_wrapper


class LogMixin:
    """
    Handy code for injecting a logger instance in any class.
    """
    @property
    def logger(self):
        global logging_handler
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


def set_logging(filename="system.log", new_session=False, level=logging.DEBUG):
    """
    This function setups the root logging system for use with the logging mixin.
    All log statements gets written to a log file
    :param filename: the name of the log file
    :param new_session: whether to delete all previous log files in the log directory
    :param level: maximum log level to log for
    """
    global logging_handler
    log_dir = os.path.abspath(config.LOG_DIRECTORY)
    make_directory(log_dir, pre_delete=new_session)

    new_file_path = os.path.join(log_dir, filename)

    logging_handler = logging.FileHandler(new_file_path)
    logging_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
    logging.basicConfig(level=level)


class ProjectTypeHints:
    Real = Union[float, int]
    Reals = List[Real]
    Numbers = Union[Reals, Real]
    Countable_Sequence = Union[List[Any], Tuple[Any,...]]
    ODE_Function = Callable[[Numbers, Numbers], Numbers]
