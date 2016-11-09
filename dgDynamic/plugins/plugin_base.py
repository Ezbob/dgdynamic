import abc
import csv
from ..utils.project_utils import LogMixin
from dgDynamic.utils.project_utils import make_directory
import threading
import time
import os.path
import multiprocessing as mp
from dgDynamic.config.settings import config
from dgDynamic.utils.plotter import plot


class SimulationOutput(LogMixin):

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
            if isinstance(abstract_system.symbols, dict):
                self.symbols = tuple(abstract_system.symbols.values())
            elif isinstance(abstract_system.symbols, (tuple, list, set)):
                self.symbols = abstract_system.symbols
            else:
                self.symbols = None
        else:
            self.symbols = None

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self, filename=None, labels=None, figure_size=None, axis_labels=None, axis_limits=None, title=None,
             should_wait=False, timeout=10):
        if title is None:
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
                # writing header underscore prefix marks that the columns where ignored (for ODE only, since SPiM
                # don't output data for a variable if it's not in the plot directive)
                out.write(header_row())

                for row in gen_data_rows():
                    out.write(row)
            end_t = time.time()
            self.logger.info("Finished writing to disk. Took: {} secs".format(end_t - start_t))

        self._file_writer_thread = threading.Thread(target=write_data)
        self._file_writer_thread.start()

        return self


class PluginBase(abc.ABC, LogMixin):

    def __init__(self, simulation_range, initial_conditions, parameters):
        self.simulation_range = simulation_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions

    @abc.abstractmethod
    def solve(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def __call__(self, simulation_range, initial_conditions, parameters):
        pass
