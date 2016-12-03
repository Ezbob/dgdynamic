import numpy as np
from dgDynamic.output import SimulationOutput


class DynamicAnalytics:
    def __init__(self, simulation_output: SimulationOutput):
        self.output = simulation_output

    def generate_fourier_transformations(self, windowing_function=None, *args, **kwargs):
        for dependent_index in range(self.output.dependent_dimension):
            numpy_array = np.fromiter((self.output.dependent[index][dependent_index]
                                       for index in range(len(self.output))), dtype=float)
            if windowing_function:
                yield np.fft.rfft(numpy_array * windowing_function(len(numpy_array)), *args, **kwargs)
            else:
                yield np.fft.rfft(numpy_array, *args, **kwargs)

    def generate_amplitude_spectrum(self, specific_index=None, windowing_function=None, *args, **kwargs):

        def cycle_through_transformations(index, windowing_function=None, *args, **kwargs):
            if 0 > specific_index:
                raise ValueError("Specific index cannot be negative")
            elif specific_index > len(self.output.dependent[0]) - 1:
                raise ValueError("Specific index exceeds the dimension of the dependent values")

            transformation = None
            generator = self.generate_fourier_transformations(windowing_function, *args, **kwargs)
            for trans_index, fourier_trans in enumerate(generator):
                if index == trans_index:
                    transformation = fourier_trans
                    break
            if not transformation:
                raise ValueError("specific index not found")
            return transformation

        if specific_index:
            specific_transformation = cycle_through_transformations(specific_index,
                                                                    windowing_function=windowing_function,
                                                                    *args, **kwargs)
            yield np.abs(specific_transformation) / len(self.output.dependent)

        else:
            for fourier_trans in self.generate_fourier_transformations(windowing_function, *args, **kwargs):
                yield np.abs(fourier_trans) / len(self.output.dependent)

    def generate_power_spectrum(self, specific_index=None, windowing_function=None, *args, **kwargs):
        def cycle_through_transformations(index, windowing_function=None, *args, **kwargs):
            if 0 > specific_index:
                raise ValueError("Specific index cannot be negative")
            elif specific_index > len(self.output.dependent[0]) - 1:
                raise ValueError("Specific index exceeds the dimension of the dependent values")

            transformation = None
            generator = self.generate_fourier_transformations(windowing_function, *args, **kwargs)
            for trans_index, fourier_trans in enumerate(generator):
                if index == trans_index:
                    transformation = fourier_trans
                    break
            if not transformation:
                raise ValueError("specific index not found")
            return transformation

        if specific_index:
            specific_transformation = cycle_through_transformations(specific_index,
                                                                    windowing_function=windowing_function,
                                                                    *args, **kwargs)
            yield (np.abs(specific_transformation) / len(self.output.dependent)) ** 2

        else:
            for fourier_trans in self.generate_fourier_transformations(windowing_function, *args, **kwargs):
                yield (np.abs(fourier_trans) / len(self.output.dependent)) ** 2

