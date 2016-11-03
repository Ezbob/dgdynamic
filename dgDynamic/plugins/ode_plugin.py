import os
import os.path
import threading
import time
from abc import abstractmethod, ABCMeta
from enum import Enum
import multiprocessing as mp
import sympy as sp
from typing import Union, Dict, Tuple, Callable
from dgDynamic.config.settings import config
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.utils.project_utils import LogMixin, make_directory, ProjectTypeHints as Types
from ..utils.plotter import plot


def sanity_check(plugin_instance, initial_values):
    if plugin_instance.integration_range is None:
        raise ValueError("Integration range not set")
    elif len(plugin_instance.integration_range) != 2:
        raise ValueError("Integration range; tuple is not of length 2")
    elif plugin_instance.integration_range[0] > plugin_instance.integration_range[1]:
        raise ValueError("First value exceeds second in integration range")
    elif initial_values is None:
        raise ValueError("No valid or no initial condition values where given")
    elif len(initial_values) - initial_values.count(None) < plugin_instance.ode_count:
        raise ValueError("Not enough initial values given")
    elif len(initial_values) - initial_values.count(None) > plugin_instance.ode_count:
        raise ValueError("Too many initial values given")
    elif plugin_instance.parameters is None:
        raise ValueError("Parameters not set")
    elif plugin_instance._reaction_count != _count_parameters(plugin_instance.parameters):
        raise ValueError("Expected {} parameter values, have {}".format(plugin_instance._reaction_count,
                                                                        _count_parameters(plugin_instance.parameters)))


def _count_parameters(parameters):
    return sum(2 if "<=>" in reaction_string else 1 for reaction_string in parameters.keys())


def get_initial_values(initial_conditions, symbols):
    if isinstance(initial_conditions, (tuple, list)):
        return initial_conditions
    elif isinstance(initial_conditions, dict):
        translate_mapping = {val: index for index, val in enumerate(symbols.values())}
        results = [0] * len(translate_mapping)
        for key, value in initial_conditions.items():
            key_symbol = sp.Symbol(key)
            if key_symbol in translate_mapping:
                results[translate_mapping[key_symbol]] = value
        return results


class OdePlugin(metaclass=ABCMeta):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def __init__(self, function: Union[object, Callable, str]=None, integration_range=(0, 0), initial_conditions=None,
                 delta_t=0.05, parameters=None, species_count=1, initial_t=0, converter_function=None,
                 ode_solver=None):

        if type(function) is ODESystem:
            self.ode_count = function.species_count
            self._reaction_count = function.reaction_count
            self._symbols = function.symbols
            self._abstract_system = function
            self.ignored_count = len(function.ignored)
            self._ignored = function.ignored
            self._user_function = None
        else:
            self._ignored = ()
            self.ignored_count = 0
            self._reaction_count = None
            self.ode_count = species_count
            self._abstract_system = None
            self._symbols = None
            self._user_function = function

        self.initial_t = initial_t
        self._ode_solver = ode_solver
        self.delta_t = delta_t
        self.parameters = parameters
        self.integration_range = integration_range
        self.initial_conditions = initial_conditions
        self._convert_to_function(converter_function)

    def _convert_to_function(self, converter_function):
        if type(self._abstract_system) is ODESystem and callable(converter_function) and \
                        self.parameters is not None:
            self._user_function = converter_function(self._abstract_system, self.parameters)

    def __call__(self, ode_solver=None, integration_range=None, initial_conditions=None, parameters=None, **kwargs):
        self.ode_solver = ode_solver
        self.integration_range = integration_range
        self.initial_conditions = initial_conditions
        self.parameters = parameters
        output = self.solve(**kwargs)
        if output is None:
            raise ValueError("Solve returned None; check the calling parameters")
        return output

    @abstractmethod
    def solve(self, **kwargs) -> object:
        pass

    @property
    def ode_solver(self):
        return self._ode_solver

    @ode_solver.setter
    def ode_solver(self, solver: Enum):
        self._ode_solver = solver

    def set_ode_solver(self, solver: Enum):
        self.ode_solver = solver
        return self

    def set_integration_range(self, *range_tuple: Tuple[int, int]):
        if isinstance(range_tuple, tuple):
            if type(range_tuple[0]) is tuple:
                self.integration_range = range_tuple[0]
            else:
                self.integration_range = range_tuple
        return self

    def set_parameters(self, parameters: Union[list, tuple, Dict[str, float]]):
        self.parameters = parameters
        return self

    def set_abstract_ode_system(self, system: ODESystem):
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
    def __init__(self, solved_by, dependent, independent, ignore=(), solver_method=None, abstract_system=None):
        self.dependent = dependent
        self.independent = independent
        self.solver_used = solved_by
        self.solver_method_used = solver_method
        self._data_filename = "data"
        self._ignored = tuple(item[1] for item in ignore)
        self._path = os.path.abspath(config['Output Paths']['DATA_DIRECTORY'])
        self._file_writer_thread = None

        if abstract_system is not None:
            self.symbols = tuple(abstract_system.symbols.values())
        else:
            self.symbols = None

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self, filename=None, labels=None, figure_size=None, axis_labels=None, axis_limits=None, should_wait=False,
             timeout=10):
        title = self.solver_used.name.title()
        if self.solver_method_used is not None:
            title += (" - " + self.solver_method_used.name)

        # using queue here it's process-safe
        queue = mp.Queue()
        queue.put({
            'independent': self.independent,
            'dependent': self.dependent,
            'symbols': self.symbols,
            'ignored': self._ignored,
            'title': title,
            'filename': filename,
            'labels': labels,
            'figure_size': figure_size,
            'axis_labels': axis_labels,
            'axis_limits': axis_limits,
        })
        process = mp.Process(target=plot, args=(queue,))
        process.start()
        if should_wait:
            process.join(timeout=timeout)
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

    def save(self, name=None, float_precision=12, prefix=None, unfiltered=False, stream=None):
        """
        Saves the independent and dependent variables as a Tab Separated Variables(TSV) file in the directory specified
        by the DATA_DIRECTORY variable in the configuration file. The name of the TSV file is constructed from a
        concatenation of the ODE solver name followed by a underscore, the 'name' parameter and finally the file
        extension.
        :param prefix: name prefix for the data file
        :param unfiltered: whether to mark 'unchanging species' in the output data set
        :param name: a name for the data file
        :param stream: use another stream than a file stream
        :param float_precision: precision when printing out the floating point numbers
        :return:
        """
        name = self._data_filename if name is None else name

        if len(self.dependent) == 0 or len(self.independent) == 0:
            raise ValueError("No or mismatched data")
        self._data_filename = name if name is not None and type(name) is str else self._data_filename

        if unfiltered:
            paired_data = zip(self.independent, self.dependent)
        else:
            paired_data = zip(self.independent, self._filter_out_ignores())

        make_directory(config['Output Paths']['DATA_DIRECTORY'], pre_delete=False)

        dependent_dimension = 0
        try:
            if unfiltered:
                dependent_dimension = len(self.dependent[0])
            else:
                dependent_dimension = abs(len(self.dependent[0]) - len(self._ignored))
            self.logger.debug("Dimension of the dependent variable is {}".format(dependent_dimension))
        except TypeError:
            self.logger.warn("Dimension of the dependent variable could not be determined; defaulting to 0")

        def header_row():
            header = "t\t"
            for j in range(0, dependent_dimension):
                if unfiltered and j in self._ignored:
                    header += "_y{}".format(j)
                else:
                    header += "y{}".format(j)

                if j < dependent_dimension - 1:
                    header += "\t"
            header += "\n"
            return header

        new_filename = self._get_file_prefix(name, prefix=prefix)
        self.logger.info("Saving data as {}".format(new_filename))

        def gen_data_rows():
            for independent, dependent in paired_data:
                result = "{:.{}f}\t".format(independent, float_precision)
                try:
                    for index, variable in enumerate(dependent):
                        if index < dependent_dimension - 1:
                            result += "{:.{}f}\t".format(variable, float_precision)
                        else:
                            result += "{:.{}f}".format(variable, float_precision)
                except TypeError:
                    self.logger.warning("Dependent variable is not iterable")
                    try:
                        result += "{:.{}f}".format(dependent, float_precision)
                    finally:
                        self.logger.exception("Could not write dependent variable to file")
                yield result + "\n"

        if stream is None:
            stream = open(new_filename, mode='w')

        def write_data():
            self.logger.info("Started on writing data to disk")
            start_t = time.time()
            with stream as out:
                # writing header underscore prefix marks that the columns where constant in the integration process
                out.write(header_row())

                for row in gen_data_rows():
                    out.write(row)
            end_t = time.time()
            self.logger.info("Finished writing to disk. Took: {} secs".format(end_t - start_t))

        self._file_writer_thread = threading.Thread(target=write_data)
        self._file_writer_thread.start()

        return self
