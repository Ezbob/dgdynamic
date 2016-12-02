import abc
import csv
from ..utils.project_utils import LogMixin
from dgDynamic.utils.project_utils import make_directory
import threading
import time
import os.path
import matplotlib.pyplot as plt
from dgDynamic.config.settings import config
from dgDynamic.utils.plotter import plot


class PluginBase(abc.ABC, LogMixin):

    def __init__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None):
        self.simulation_range = simulation_range
        self.rate_parameters = rate_parameters
        self.initial_conditions = initial_conditions
        self.drain_parameters = drain_parameters

    @abc.abstractmethod
    def solve(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def __call__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters):
        pass
