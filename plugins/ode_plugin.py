import matplotlib.pyplot as plt
import logging
import os
import os.path
import shutil
import config
from abc import abstractmethod, ABCMeta


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


class OdePlugin(metaclass=ABCMeta):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """
    def __init__(self, function=None, integration_range=(0, 0), initial_conditions=None, delta_t=0.05):
        self._user_function = function
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
    """
    The output class for the ODE plugins. This class specifies the handling of solution output from any of the
    ODE plugins. It is the responsibility of the individual ODE plugin to produce a set of independent and dependent
     variables that has the right type format for the printing and plotting methods.
    """
    def __init__(self, solved_by, dependent, independent):
        self.dependent = dependent
        self.independent = independent
        self.solver = solved_by

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self):
        plt.plot(self.independent, self.dependent)
        plt.show()
        return self

    def save(self, name="data", float_precision=8):
        """
        Saves the independent and dependent variables as a Tab Separated Variables(TSV) file in the directory specified
        by the DATA_DIRECTORY variable in the configuration file. The name of the TSV file is constructed from a
        concatenation of the ODE solver name followed by a underscore, the 'name' parameter and finally the file
        extension.
        :param name: a name for the data file
        :param float_precision: precision when printing out the floating point numbers
        :return:
        """
        paired_data = zip(self.independent, self.dependent)
        _make_directory(config.DATA_DIRECTORY, pre_delete=False)

        dependent_dimension = 0
        if isinstance(self.dependent, list) and isinstance(self.dependent[0], list):
            dependent_dimension = len(self.dependent[0])
            self.logger.debug("Dimension of the dependent variable is {}".format(dependent_dimension))

        absolute = os.path.abspath(config.DATA_DIRECTORY)
        new_filename = os.path.join(absolute, "{}_{}.tsv".format(self.solver.value, name))
        self.logger.debug("Saving data as {}".format(new_filename))

        with open(new_filename, mode='w') as fileout:
            # writing header
            fileout.write("t\t")
            for j in range(0, dependent_dimension - 1):
                fileout.write("y{}\t".format(j))
            fileout.write("y{}\n".format(dependent_dimension - 1))

            # now for the data
            for independent, dependent in paired_data:
                # here the dimension of the independent variable is assumed to be 1 since it's a ODE
                fileout.write("{:.{}f}\t".format(independent, float_precision))

                for index, variable in enumerate(dependent):
                    if index < dependent_dimension - 1:
                        fileout.write("{:.{}f}\t".format(variable, float_precision))
                    else:
                        fileout.write("{:.{}f}".format(variable, float_precision))
                fileout.write("\n")
        return self


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
