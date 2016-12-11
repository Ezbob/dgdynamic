import abc
import csv
from ..utils.project_utils import LogMixin
from dgDynamic.utils.project_utils import make_directory
import threading
import time
import os.path
import matplotlib.pyplot as plt
from dgDynamic.config.settings import config
from dgDynamic.utils.plotter import matplotlib_plot


class PluginBase(abc.ABC, LogMixin):

    @abc.abstractmethod
    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        return self.simulate(simulation_range=simulation_range, initial_conditions=initial_conditions,
                             rate_parameters=rate_parameters, drain_parameters=drain_parameters, *args, **kwargs)
