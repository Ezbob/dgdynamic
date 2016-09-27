import logging
import config
import os
import shutil


def debug_printer(function):
    """
    Use this function as decorator
    :param function: the function that has been decorated
    :return: the wrapper that decorates the function
    """
    def debug_wrapper(*args, **kwargs):
        print("Now entering function {} with arguments {} and\
keyword arguments {}".format(function.__name__(), args, kwargs))
        function(args, kwargs)
        print("Leaving function {}".format(args))
    return debug_wrapper


class LogMixin:
    """
    Handy code for injecting a logger instance in any class.
    """
    @property
    def logger(self):
        name = ".".join([__name__, self.__class__.__name__])
        return logging.getLogger(name)


def make_directory(path, pre_delete=False):
    if os.path.exists(path) and pre_delete is True:
            shutil.rmtree(path)
            os.mkdir(path)
    elif not os.path.exists(path):
        os.mkdir(path)


def set_logging(filename="solver.log", new_session=False, level=logging.DEBUG):
    """
    This function setups the root logging system for use with the logging mixin.
    All log statements gets written to a log file
    :param filename: the name of the log file
    :param new_session: whether to delete all previous log files in the log directory
    :param level: maximum log level to log for
    """
    log_dir = os.path.abspath(config.LOG_DIRECTORY)
    make_directory(log_dir, pre_delete=new_session)
    new_file_path = os.path.join(log_dir, filename)
    logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filename=new_file_path, filemode='w')
