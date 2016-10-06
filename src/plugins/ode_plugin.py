import os
import os.path
from abc import abstractmethod, ABCMeta
import matplotlib.pyplot as plt
import config
from enum import Enum
from src.utils.project_utils import LogMixin, make_directory, ProjectTypeHints as Types
from src.mod_interface.ode_generator import dgODESystem
from typing import Union, Dict, Tuple, Callable
import sympy as sp
from ..utils.project_utils import ProjectTypeHints
from collections import OrderedDict
from os.path import commonprefix


def sanity_check(plugin_instance, initial_values):
    if plugin_instance.integration_range is None:
        raise ValueError("Integration range not set")
    elif len(plugin_instance.integration_range) != 2:
        raise ValueError("Integration range; tuple is not of length 2")
    elif plugin_instance.integration_range[0] > plugin_instance.integration_range[1]:
        raise ValueError("First value exceeds second in integration range")
    elif initial_values is None:
        raise ValueError("No valid or no initial condition values where given")
    elif len(initial_values) < plugin_instance.ode_count:
        raise ValueError("Not enough initial values given")
    elif len(initial_values) > plugin_instance.ode_count:
        raise ValueError("Too many initial values given")
    elif plugin_instance.parameters is None:
        raise ValueError("Parameters not set")


def _match_and_set_on_commonprefix(translater_dict: dict, prefix: str, value: Types.Real, results: list):
    got_prefix = (symbol_key for symbol_key in translater_dict.keys() if
                  commonprefix((prefix, str(symbol_key))))
    for symbol in got_prefix:
        results[translater_dict[symbol]] = value


def get_initial_values(initial_conditions, symbols):
    if isinstance(initial_conditions, (tuple, list)):
        return initial_conditions
    elif isinstance(initial_conditions, dict):
        translate_mapping = {val: index for index, val in enumerate(symbols.values())}
        results = [0] * len(translate_mapping)
        for key, value in initial_conditions.items():
            try:
                results[translate_mapping[sp.Symbol(key)]] = value
            except KeyError as error:
                try:
                    _match_and_set_on_commonprefix(translate_mapping, key, value, results)
                except KeyError:
                    raise KeyError("Unknown initial value for symbol: {}".format(", ".join(map(str, error.args))))

        return results


class OdePlugin(metaclass=ABCMeta):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def __init__(self, function: Union[object, Callable, str]=None, integration_range=(0, 0), initial_conditions=None,
                 delta_t=0.05, parameters=None, species_count=1, initial_t=0, converter_function=None,
                 solver_method=None):

        if type(function) is dgODESystem:
            self.ode_count = function.species_count
            self._symbols = function.symbols
            self.ignored_count = len(function.ignored)
            self._ignored = function.ignored
        else:
            self._ignored = ()
            self.ignored_count = 0
            self.ode_count = species_count

        self.initial_t = initial_t
        self._ode_solver = solver_method

        if type(function) is dgODESystem:
            self._abstract_system = function
            self._symbols = function.symbols
            self._user_function = None
        else:
            self._abstract_system = None
            self._symbols = None
            self._user_function = function

        self.delta_t = delta_t
        self.parameters = parameters
        self.integration_range = integration_range
        self.initial_conditions = initial_conditions
        self._convert_to_function(converter_function)

    def _convert_to_function(self, converter_function):
        if type(self._abstract_system) is dgODESystem and callable(converter_function) and \
                        self.parameters is not None:
            self._user_function = converter_function(self._abstract_system, self.parameters)

    @abstractmethod
    def solve(self) -> object:
        pass

    def set_ode_solver(self, solver: Enum):
        self._ode_solver = solver

    def set_integration_range(self, *range_tuple: Tuple[int, int]):
        arg = []
        if isinstance(range_tuple, tuple):
            if type(range_tuple[0]) is tuple:
                self.integration_range = range_tuple[0]
            else:
                self.integration_range = range_tuple
        return self

    def set_parameters(self, parameters: Union[list, tuple, Dict[str, float]]):
        self.parameters = parameters
        return self

    def set_abstract_ode_system(self, system: dgODESystem):
        self._abstract_system = system
        self.ode_count = system.species_count
        self.ignored_count = len(system.ignored)
        self._ignored = system.ignored
        self._symbols = system.symbols
        return self

    def set_initial_conditions(self, conditions: Dict[str, Types.Reals]):
        self.initial_conditions = conditions
        return self

    def set_ode_function(self, ode_function: Types.ODE_Function):
        self._user_function = ode_function
        return self


class OdeOutput(LogMixin):
    """
    The output class for the ODE plugins. This class specifies the handling of solution output from any of the
    ODE plugins. It is the responsibility of the individual ODE plugin to produce a set of independent and dependent
     variables that has the right type format for the printing and plotting methods.
    """
    def __init__(self, solved_by, dependent, independent, ignore=()):
        self.dependent = dependent
        self.independent = independent
        self.solver_used = solved_by
        self._data_filename = "data"
        self._ignored = tuple(item[1] for item in ignore)
        self._path = os.path.abspath(config.DATA_DIRECTORY)

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self, filename=None, linestyle='-', labels=None, figure_size=None):
        """
        Tries to plot the data using the MatPlotLib
        :return: self (chaining enabled)
        """
        if len(self.dependent) == 0 or len(self.independent) == 0:
            raise ValueError("No or mismatched data")

        lines = plt.plot(self.independent, tuple(self._filter_out_ignores()), linestyle)
        plt.tight_layout()

        if labels is not None:
            assert len(labels) >= len(lines)
            for index, line in enumerate(lines):
                line.set_label(labels[index])
            plt.legend()

        if figure_size is not None:
            assert len(figure_size) >= 2

            def cm2inch(number): return number / 2.54

            fig = plt.gcf()
            fig.set_size_inches(cm2inch(figure_size[0]), cm2inch(figure_size[1]), forward=True)


        plt.title(self.solver_used.value)
        if filename is None or type(filename) is not str:
            plt.show()
        else:
            plt.savefig(filename, bbox_inches='tight')
        return self

    def _get_file_prefix(self, name, extension=".tsv", prefix=None):
        if prefix is None:
            return os.path.join(self._path, "{}_{}{}".format(self.solver_used.value, name, extension))
        else:
            return os.path.join(self._path, "{}{}{}".format(prefix, name, extension))

    def _filter_out_ignores(self):
        for rows in self.dependent:
            filtered_row = ()
            for index, item in enumerate(rows):
                if index not in self._ignored:
                    filtered_row += (item,)
            yield filtered_row

    def save(self, name=None, float_precision=12, prefix=None):
        """
        Saves the independent and dependent variables as a Tab Separated Variables(TSV) file in the directory specified
        by the DATA_DIRECTORY variable in the configuration file. The name of the TSV file is constructed from a
        concatenation of the ODE solver name followed by a underscore, the 'name' parameter and finally the file
        extension.
        :param name: a name for the data file
        :param float_precision: precision when printing out the floating point numbers
        :return:
        """
        name = self._data_filename if name is None else name

        if len(self.dependent) == 0 or len(self.independent) == 0:
            raise ValueError("No or mismatched data")
        self._data_filename = name if name is not None and type(name) is str else self._data_filename

        paired_data = zip(self.independent, self._filter_out_ignores())
        make_directory(config.DATA_DIRECTORY, pre_delete=False)

        dependent_dimension = 0
        try:
            dependent_dimension = abs(len(self.dependent[0]) - len(self._ignored))
            self.logger.debug("Dimension of the dependent variable is {}".format(dependent_dimension))
        except TypeError:
            self.logger.warn("Dimension of the dependent variable could not be determined; defaulting to 0")

        new_filename = self._get_file_prefix(name, prefix=prefix)
        self.logger.info("Saving data as {}".format(new_filename))

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
