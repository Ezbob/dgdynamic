import numpy as np
from dgDynamic.output import SimulationOutput
from dgDynamic.utils.project_utils import pop_or_default


class DynamicAnalytics:
    def __init__(self, simulation_output: SimulationOutput, sample_rate=None):
        self.output = simulation_output
        self.windowing_function = np.hanning
        self.sample_size = len(self.output.dependent)
        # default: assuming uniform spacing between time samples
        self.sample_rate = self.sample_size / self.output.simulation_duration \
            if sample_rate is None else sample_rate

    def generate_fourier_transformations(self, bins=None, normalize_with=None, *args, **kwargs):
        for dependent_index in range(self.output.dependent_dimension):
            numpy_array = np.fromiter((self.output.dependent[index][dependent_index]
                                       for index in range(len(self.output))), dtype=float)
            if self.windowing_function is not None:
                window_convolution = numpy_array * self.windowing_function(self.sample_size)
                if normalize_with is None:
                    yield np.fft.rfft(window_convolution, n=bins, *args, **kwargs)
                else:
                    yield np.fft.rfft(window_convolution, n=bins, *args, **kwargs) / normalize_with
            else:
                if normalize_with is None:
                    yield np.fft.rfft(numpy_array, n=bins, *args, **kwargs)
                else:
                    yield np.fft.rfft(numpy_array, n=bins, *args, **kwargs) / normalize_with

    def generate_amplitude_spectrum(self, with_freqs=False, *args, **kwargs):
        sample_spacing = pop_or_default(kwargs, 'd', default=1.0)
        for fourier_trans in self.generate_fourier_transformations(*args, **kwargs):
            amplitudes = np.abs(fourier_trans) / self.sample_size
            if with_freqs:
                yield amplitudes, np.fft.rfftfreq(self.sample_size, d=sample_spacing)
            else:
                yield amplitudes

    def generate_power_spectrum(self, with_freqs=False, *args, **kwargs):
        sample_spacing = pop_or_default(kwargs, 'd', default=1.0)
        for trans in self.generate_fourier_transformations(*args, **kwargs):
            power_spectrum = (np.abs(trans) / self.sample_size) ** 2
            if with_freqs:
                yield power_spectrum, np.fft.rfftfreq(self.sample_size, d=sample_spacing)
            else:
                yield power_spectrum

    def get_power_spectrum(self, *args, **kwargs):
        return tuple(self.generate_power_spectrum(*args, **kwargs))

    def get_amplitude_spectrum(self, with_freqs=False, *args, **kwargs):
        if with_freqs:
            instance = tuple(self.generate_amplitude_spectrum(with_freqs=with_freqs, *args, **kwargs))
            return tuple(amp_set[0] for amp_set in instance), tuple(amp_set[1] for amp_set in instance)
        else:
            return tuple(self.generate_amplitude_spectrum(with_freqs=with_freqs, *args, **kwargs))

