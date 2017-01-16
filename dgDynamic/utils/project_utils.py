import logging
import os
import shutil
import time
from .logger import logging_handler
import sys
import itertools as it
import threading


def pop_or_default(kwargs, key, default=None):
    try:
        return kwargs.pop(key)
    except KeyError:
        return default


def spin_it(message, frames=('|', '\\', '-', '/'), delay_scale=1):
    def inner(function):
        def do_function(*args, **kwargs):
            sys.stdout.write(message)
            spinner = Spinner(frames=frames, delay=delay_scale)
            spinner.start()
            output = function(*args, **kwargs)
            spinner.stop()
            sys.stdout.write('\n')
            return output
        return do_function
    return inner


class Spinner:
    def __init__(self, frames=('|', '\\', '-', '/'), delay=1, stream=None):
        self.frames = it.cycle(frames)
        self.number_of_frames = len(frames)
        self.delay = delay
        self.stream = sys.stdout if stream is None else stream
        self.is_running = True
        self.thread = None

    def start(self):
        def do_it():
            while self.is_running:
                self.stream.write("{}\n".format(next(self.frames)))
                self.stream.flush()
                time.sleep(1 / self.number_of_frames * self.delay)
                self.stream.write('\b\b')
        self.thread = threading.Thread(target=do_it)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()


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

