import logging
import config
import os
import shutil
import time
from typing import *
logging_handler = None


def log_it(function):
    """
    Use this function as decorator, to enable logging for a function
    :param function: the function that has been decorated
    :return: the wrapper that decorates the function
    """
    global logging_handler
    name = ".".join([function.__module__, function.__name__])
    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)

    def debug_wrapper(*args, **kwargs):
        logger.info("Now entering function {} with arguments {} and\
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


def set_logging():
    """
    This function setups the root logging system for use with the logging mixin.
    All log statements gets written to a log file
    :param filename: the name of the log file
    :param new_session: whether to delete all previous log files in the log directory
    :param level: maximum log level to log for
    """
    global logging_handler
    if logging_handler is None:
        log_dir_name = config.LOG_DIRECTORY if config.LOG_DIRECTORY else "logs"
        filename = config.SYSTEM_LOG_FILE if config.SYSTEM_LOG_FILE else "system.log"
        level = config.LOG_LEVEL if isinstance(config.LOG_LEVEL, type(logging.INFO)) else logging.INFO
        new_session = not config.SAVE_LOGS if isinstance(config.SAVE_LOGS, bool) else False

        log_dir = os.path.abspath(log_dir_name)
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

set_logging()