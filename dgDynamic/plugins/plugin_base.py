import abc
from ..utils.project_utils import LogMixin


class OutputBase(abc.ABC, LogMixin):

    @abc.abstractmethod
    def plot(self):
        pass

    @abc.abstractmethod
    def save(self):
        pass


class PluginBase(abc.ABC, LogMixin):

    def __init__(self, initial_conditions, parameters):
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
    def __call__(self, initial_conditions, parameters):
        pass
