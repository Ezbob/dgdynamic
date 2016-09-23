import matplotlib.pyplot as plt
import logging
import os
import os.path
import shutil
import config
import abc
from abc import abstractmethod


class LogMixin:
    """
    Handy code for injecting a logger instance in any class
    """
    @property
    def logger(self):
        name = ".".join([__name__, self.__class__.__name__])
        return logging.getLogger(name)


class OdePlugin(metaclass=abc.ABCMeta):
    def __init__(self, function=None, integration_range=(0, 0), initial_conditions=None, delta_t=0.05):
        self.user_function = function
        self.delta_t = delta_t

        if isinstance(integration_range, (tuple, list)) and len(integration_range) >= 2:
            self.integration_range = integration_range
        if initial_conditions is None:
            self.initial_conditions = {0: 0}
        elif isinstance(initial_conditions, dict):
            self.initial_conditions = initial_conditions

    @abstractmethod
    def set_integration_range(self, range_tuple):
        raise NotImplementedError("Subclass must implement abstract method")

    @abstractmethod
    def set_ode_method(self, name):
        raise NotImplementedError("Subclass must implement abstract method")

    @abstractmethod
    def set_initial_conditions(self, conditions):
        raise NotImplementedError("Subclass must implement abstract method")

    @abstractmethod
    def solve(self):
        raise NotImplementedError("Subclass must implement abstract method")

    @abstractmethod
    def set_ode_function(self, ode_function):
        raise NotImplementedError("Subclass must implement abstract method")


class OdeOutput(LogMixin):
    def __init__(self, solved_by, dependent, independent):
        self.dependent = dependent
        self.independent = independent
        self.solver = solved_by

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self):
        ys = list(self.dependent)
        ts = list(self.independent)
        plt.plot(ts, ys)
        plt.show()

    def save(self, name="plotdata"):
        paired = list(zip(self.independent, self.dependent))
        _make_directory(config.DATA_DIRECTORY, pre_delete=False)
        count = 0
        if isinstance(self.dependent, list) and isinstance(self.dependent[0], list):
            count = len(self.dependent[0])
            self.logger.debug("Count is {}".format(count))

        absolute = os.path.abspath(config.DATA_DIRECTORY)
        new_filename = os.path.join(absolute, "{}_{}.tsv".format(self.solver.value, name))
        self.logger.debug("Saving data as {}".format(new_filename))
        with open(new_filename, mode='w') as fout:
            # writing header
            fout.write("t\t")
            for j in range(0, count - 1):
                fout.write("y{}\t".format(j))
            fout.write("y{}\n".format(count - 1))

            # now for the data
            for i in range(0, len(paired)):
                fout.write("{}\t".format(self.independent[i]))
                for j in range(0, count):
                    if j < count - 1:
                        fout.write("{}\t".format(self.dependent[i][j]))
                    else:
                        fout.write("{}".format(self.dependent[i][j]))
                fout.write("\n")


def _flatten(li):
    return [item for item in li]


def _unpack_matlab_double(double):
    for i in range(0, len(double._data)):
        yield double._data[i]


def _make_directory(path, pre_delete=False):
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
    _make_directory(log_dir, pre_delete=new_session)
    new_file_path = os.path.join(log_dir, filename)
    logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filename=new_file_path, filemode='w')
