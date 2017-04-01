from dgdynamic.utils.project_utils import LogMixin, make_directory
from dgdynamic.config.settings import config
from dgdynamic.utils.plotter import matplotlib_plot
from scipy.interpolate import interpolate
import threading
import time
import csv
import matplotlib.pyplot as plt
import os.path
import enum
import collections
import array
import numpy


class SimulationOutput(LogMixin):

    def __init__(self, solved_by, user_sim_range, symbols, dependent=(), independent=(), ignore=(),
                 solver_method=None, errors=(),):
        self.dependent = numpy.asanyarray(dependent, dtype=float)
        self.independent = numpy.asanyarray(independent, dtype=float)
        self.errors = errors
        self.solver_used = solved_by
        self.solver_method_used = solver_method
        self.requested_simulation_range = user_sim_range

        if independent is not None and len(independent) >= 2:
            self.simulation_duration = abs(independent[-1] - independent[0])
        elif independent is not None and len(independent) == 1:
            self.simulation_duration = independent[0]
        else:
            self.simulation_duration = 0.0

        try:
            self._ignored = tuple(item[1] for item in ignore)
        except IndexError:
            self._ignored = ignore
        self._path = os.path.abspath(config['Output Paths']['DATA_DIRECTORY'])
        self._file_writer_thread = None
        self.symbols = tuple(symbols) if isinstance(symbols, collections.Generator) else symbols

    def has_sim_prematurely_stopped(self, rel_tol=1e-05, abs_tol=1e-08):
        if len(self.independent) > 0:
            return not numpy.isclose(self.independent[-1], self.requested_simulation_range[1],
                                     rtol=rel_tol, atol=abs_tol)
        else:
            return self.requested_simulation_range[1] != 0

    def is_data_equally_spaced(self, rel_tol=1e-05, abs_tol=1e-08):
        delta_t = 0
        time_vals = self.independent
        if len(time_vals) >= 2:
            delta_t = abs(time_vals[1] - time_vals[0])
        for i in range(1, len(time_vals)):
            curr_t = time_vals[i]
            if i < len(time_vals) - 1:
                next_t = time_vals[i + 1]
                curr_dt = abs(next_t - curr_t)
                if not numpy.isclose(curr_dt, delta_t, rtol=rel_tol, atol=abs_tol):
                    return False
        return True

    def interpolate_data(self, new_sample_resolution, kind='linear'):
        """Shall return a new evenly spaced interpolated version of the original output"""
        if new_sample_resolution > 0:
            new_independent = numpy.linspace(self.independent[0], self.independent[-1], num=new_sample_resolution)
            interpolation_func = interpolate.interp1d(self.independent, self.dependent, axis=0, kind=kind)
            return SimulationOutput(self.solver_used, self.requested_simulation_range, self.symbols,
                                    dependent=interpolation_func(new_independent), independent=new_independent,
                                    ignore=self._ignored, solver_method=self.solver_method_used, errors=self.errors)
        return self

    @property
    def is_output_set(self):
        return False

    @property
    def has_errors(self):
        return len(self.errors) > 0

    @property
    def is_empty(self):
        return len(self.independent) + len(self.dependent) == 0

    @property
    def dependent_dimension(self):
        return len(self.dependent[0])

    def plot(self, filename=None, labels=None, figure_size=None, axis_labels=None,
             axis_limits=None, title=None, show_grid=True, has_tight_layout=True):
        if title is None and isinstance(self.solver_used, (str, enum.Enum)):
            if isinstance(self.solver_used, enum.Enum):
                title = self.solver_used.name.title()
            else:
                title = self.solver_used
            if self.solver_method_used is not None:
                title += (" - " + self.solver_method_used.name)

        input_values = {
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
            'show_grid': show_grid,
            'has_tight_layout': has_tight_layout,
        }
        matplotlib_plot(input_values)
        return self

    @staticmethod
    def show(*args, **kwargs):
        plt.show(*args, **kwargs)

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

    @property
    def filtered_output(self):
        return SimulationOutput(self.solver_used,
                                dependent=tuple(self._filter_out_ignores()),
                                independent=self.independent, ignore=(),
                                solver_method=self.solver_method_used,
                                symbols=self.symbols, errors=self.errors,
                                user_sim_range=self.requested_simulation_range)

    def save(self, filename, prefix=None, unfiltered=False, labels=None, stream=None):
        """
        Saves the independent and dependent variables as a Tab Separated Variables(TSV) file in the directory specified
        by the DATA_DIRECTORY variable in the configuration file. The name of the TSV file is constructed from a
        concatenation of the ODE solver name followed by a underscore, the 'name' parameter and finally the file
        extension.
        :param prefix: name prefix for the data file. Default is the plugin name followed by an underscore.
        :param unfiltered: whether to mark 'unchanging species' in the output data set
        :param filename: a name for the data file
        :param stream: use another stream than a file stream
        :param labels: use custom header labels for species. Default is the symbols specified by the model.
        :return:
        """
        float_precision = config.getint('Simulation', 'FIXED_POINT_PRECISION', fallback=18)

        if len(self.dependent) == 0 or len(self.independent) == 0:
            self.logger.warn("No or mismatched data")
            return

        if unfiltered:
            paired_data = zip(self.independent, self.dependent)
        else:
            paired_data = zip(self.independent, self._filter_out_ignores())

        make_directory(config['Output Paths']['DATA_DIRECTORY'], pre_delete=False)

        if unfiltered:
            dependent_dimension = self.dependent_dimension
        else:
            dependent_dimension = max(self.dependent_dimension - len(self._ignored), 0)

        self.logger.debug("Dimension of the dependent variable is {}".format(dependent_dimension))

        header_labels = self.symbols if labels is None else labels
        assert isinstance(header_labels, (list, set, tuple))

        def header():
            assert len(header_labels) - len(self._ignored) == dependent_dimension, \
                "Expected {} number of labels got {}"\
                .format(dependent_dimension, len(header_labels))
            yield "time"
            for index, label in enumerate(header_labels):
                if unfiltered and index in self._ignored:
                    yield "_{}".format(label)
                else:
                    yield label

        def format_float(variable):
            return "{:.{}f}".format(variable, float_precision)

        def data_rows():
            for independent, dependent in paired_data:
                yield (format_float(independent),) + tuple(format_float(var) for var in dependent)

        if stream is None:
            file_path = self._get_file_prefix(filename, prefix=prefix)
            self.logger.info("Saving data as {}".format(file_path))
            stream = open(file_path, mode="w")

        def write_data():
            self.logger.info("Started on writing data to disk")
            start_t = time.time()
            with stream as outfile:
                # writing header underscore prefix marks that the columns where ignored (for ODE only, since SPiM
                # don't output data for a variable if it's not in the plot directive)
                writer = csv.writer(outfile, delimiter="\t")
                writer.writerow(element for element in header())
                for row in data_rows():
                    writer.writerow(row)
            end_t = time.time()
            self.logger.info("Finished writing to disk. Took: {} secs".format(end_t - start_t))

        self._file_writer_thread = threading.Thread(target=write_data)
        self._file_writer_thread.start()

        return self

    def __getitem__(self, index):
        return self.independent[index], self.dependent[index]

    def __iter__(self):
        for i in range(len(self.independent)):
            yield self.independent[i], self.dependent[i]

    def __len__(self):
        return (len(self.independent) + len(self.dependent)) // 2

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent,
                                                                         self.dependent)


class SimulationOutputSet(LogMixin):
    def __init__(self, output):
        self.output_set = tuple(output)

    def plot(self, filename=None, **kwargs):
        if isinstance(filename, collections.Iterable):
            for filename, output in zip(filename, self.output_set):
                output.plot(filename=filename, **kwargs)
        elif filename is None:
            for output in self.output_set:
                output.plot(filename=filename, **kwargs)
        else:
            raise TypeError("Expected an iterable collection of file names; got {}"
                            .format(type(filename)))
        return self

    def save(self, filename, **kwargs):
        if isinstance(filename, collections.Iterable):
            for filename, output in zip(filename, self.output_set):
                output.save(filename=filename, **kwargs)
        else:
            raise TypeError("Expected an iterable collection of file names; got {}"
                            .format(type(filename)))
        return self

    @property
    def is_output_set(self):
        return True

    @property
    def filtered_output(self):
        return SimulationOutputSet((out.filtered_output for out in self.output_set))

    @property
    def data_matrix(self):
        return tuple((array.array('d', column) for column in out.columns) for out in self.output_set)

    @property
    def failure_indices(self):
        return tuple(i for i, o in enumerate(self.output_set) if o.has_errors)

    @property
    def failures(self):
        return SimulationOutputSet(filter(lambda obj: not obj.has_errors, self.output_set))

    @property
    def successes(self):
        return SimulationOutputSet(filter(lambda obj: obj.has_errors, self.output_set))

    def __iter__(self):
        return self.output_set.__iter__()

    def __getitem__(self, key):
        return self.output_set.__getitem__(key)

    def __len__(self):
        return self.output_set.__len__()

    def __repr__(self):
        return "<SimulationOutputSet with {} runs>".format(self.__len__())
