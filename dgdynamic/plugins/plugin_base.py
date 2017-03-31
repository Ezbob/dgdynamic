import abc
from ..utils.project_utils import LogMixin


class PluginBase(abc.ABC, LogMixin):

    @abc.abstractmethod
    def simulate(self, end_t, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, end_t, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        return self.simulate(end_t=end_t, initial_conditions=initial_conditions,
                             rate_parameters=rate_parameters, drain_parameters=drain_parameters, *args, **kwargs)
