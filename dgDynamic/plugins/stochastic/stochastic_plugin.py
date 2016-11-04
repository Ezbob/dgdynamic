import abc


class StochasticOutput:
    pass


class StochasticPlugin(abc.ABC):

    def __init__(self, sample_range=None, parameters=None, initial_conditions=None,):
        self.sample_range = sample_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions

    @abc.abstractmethod
    def solve(self) -> StochasticOutput:
        pass

    def __call__(self, sample_range=None, parameters=None, initial_conditions=None,):
        self.sample_range = sample_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions
        output = self.solve()
        if output is None:
            raise ValueError("Stochastic simulation output was None; check your parameters")
        return output

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
