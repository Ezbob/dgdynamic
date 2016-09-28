import os
import os.path
from abc import abstractmethod, ABCMeta
import matplotlib.pyplot as plt
import config
from src.utils.project_utils import LogMixin, make_directory


class OdePlugin(metaclass=ABCMeta):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """
    def __init__(self, function=None, integration_range=(0, 0), initial_conditions=None, delta_t=0.05,
                 parameters=None):
        self._user_function = function
        self.delta_t = delta_t

        if isinstance(parameters, (list, tuple)) or parameters is None:
            self.parameters = parameters

        if isinstance(integration_range, (tuple, list)) and len(integration_range) >= 2:
            self.integration_range = integration_range
        if initial_conditions is None:
            self.initial_conditions = {0: 0}
        elif isinstance(initial_conditions, dict):
            self.initial_conditions = initial_conditions

    @abstractmethod
    def set_integration_range(self, range_tuple):
        pass

    @abstractmethod
    def set_ode_method(self, name):
        pass

    @abstractmethod
    def set_initial_conditions(self, conditions):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def set_ode_function(self, ode_function):
        pass

    @abstractmethod
    def set_parameters(self, parameters):
        pass

    @abstractmethod
    def from_abstract_ode_system(self, system):
        pass


class OdeOutput(LogMixin):
    """
    The output class for the ODE plugins. This class specifies the handling of solution output from any of the
    ODE plugins. It is the responsibility of the individual ODE plugin to produce a set of independent and dependent
     variables that has the right type format for the printing and plotting methods.
    """
    def __init__(self, solved_by, dependent, independent):
        self.dependent = dependent
        self.independent = independent
        self.solver_used = solved_by
        self._filename = "data"
        self._path = os.path.abspath(config.DATA_DIRECTORY)

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self, linestyle='-'):
        """
        Tries to plot the data using the MatPlotLib
        :return: self (chaining enabled)
        """
        plt.plot(self.independent, self.dependent, linestyle)
        plt.show()
        return self

    def _get_file_prefix(self, name, extension=".tsv"):
        return os.path.join(self._path, "{}_{}{}".format(self.solver_used.value, name, extension))

    def save(self, name="data", float_precision=12):
        """
        Saves the independent and dependent variables as a Tab Separated Variables(TSV) file in the directory specified
        by the DATA_DIRECTORY variable in the configuration file. The name of the TSV file is constructed from a
        concatenation of the ODE solver name followed by a underscore, the 'name' parameter and finally the file
        extension.
        :param name: a name for the data file
        :param float_precision: precision when printing out the floating point numbers
        :return:
        """
        self._filename = name if name is not None and type(name) is str else self._filename
        paired_data = zip(self.independent, self.dependent)
        make_directory(config.DATA_DIRECTORY, pre_delete=False)

        dependent_dimension = 0
        try:
            dependent_dimension = len(self.dependent[0])
            self.logger.debug("Dimension of the dependent variable is {}".format(dependent_dimension))
        except TypeError:
            self.logger.warn("Dimension of the dependent variable could not be determined; defaulting to 0")

        new_filename = self._get_file_prefix(name)
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

                try:
                    for index, variable in enumerate(dependent):
                        if index < dependent_dimension - 1:
                            fileout.write("{:.{}f}\t".format(variable, float_precision))
                        else:
                            fileout.write("{:.{}f}".format(variable, float_precision))
                except TypeError:
                    self.logger.warning("Dependent variable is not iterable")
                    try:
                        fileout.write("{:.{}f}".format(dependent, float_precision))
                    finally:
                        self.logger.exception("Could not write dependent variable to file")
                        fileout.close()
                        raise FloatingPointError("Could not write dependent variable to file")

                fileout.write("\n")
        return self
