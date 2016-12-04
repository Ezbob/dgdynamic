import numpy as np
from dgDynamic.output import SimulationOutput


class DynamicAnalytics:
    def __init__(self, simulation_output: SimulationOutput):
        self.output = simulation_output
        self.windowing_function = np.hanning

    def generate_fourier_transformations(self, *args, **kwargs):
        for dependent_index in range(self.output.dependent_dimension):
            numpy_array = np.fromiter((self.output.dependent[index][dependent_index]
                                       for index in range(len(self.output))), dtype=float)
            if self.windowing_function is not None:
                yield np.fft.rfft(numpy_array * self.windowing_function(len(numpy_array)), *args, **kwargs)
            else:
                yield np.fft.rfft(numpy_array, *args, **kwargs)

    def generate_amplitude_spectrum(self, *args, **kwargs):
        for fourier_trans in self.generate_fourier_transformations(*args, **kwargs):
            yield np.abs(fourier_trans) / len(self.output.dependent)

    def generate_power_spectrum(self, *args, **kwargs):
        for trans in self.generate_fourier_transformations(*args, **kwargs):
            yield (np.abs(trans) / len(self.output.dependent)) ** 2

