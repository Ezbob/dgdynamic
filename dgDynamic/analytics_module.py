import numpy as np
from dgDynamic.output import SimulationOutput
from dgDynamic.utils.project_utils import pop_or_default


class DynamicAnalytics:
    def __init__(self, simulation_output: SimulationOutput, delta_t=None, sample_rate=None, windowing_function=None):
        self.output = simulation_output
        self.windowing_function = windowing_function
        self.sample_size = len(self.output.dependent)
        # default: assuming uniform spacing between time samples
        self.sample_rate = self.sample_size / self.output.simulation_duration \
            if sample_rate is None else sample_rate
        self.sample_spacing = 1 / self.sample_rate if delta_t is None else delta_t

    def _scale_fourier(self, fourier):
        # http://stackoverflow.com/questions/15147287/numpy-wrong-amplitude-of-fftd-array
        return np.fromiter((f if index == 0 else f * 2 for index, f in enumerate(fourier)), dtype=float) \
               / self.sample_size

    def generate_fourier_transformations(self, bins=None, *args, **kwargs):
        for dependent_index in range(self.output.dependent_dimension):
            numpy_array = np.fromiter((self.output.dependent[index][dependent_index]
                                       for index in range(len(self.output))), dtype=float)
            if self.windowing_function is not None:
                window_convolution = numpy_array * self.windowing_function(self.sample_size)
                yield np.fft.rfft(window_convolution, n=bins, *args, **kwargs)
            else:
                yield np.fft.rfft(numpy_array, n=bins, *args, **kwargs)

    def generate_amplitude_spectrum(self, with_freqs=False, *args, **kwargs):
        for fourier_trans in self.generate_fourier_transformations(*args, **kwargs):
            amplitudes = self._scale_fourier(np.absolute(fourier_trans))
            if with_freqs:
                yield amplitudes, np.fft.rfftfreq(self.sample_size, d=self.sample_spacing)
            else:
                yield amplitudes

    def generate_power_spectrum(self, with_freqs=False, *args, **kwargs):
        for trans in self.generate_fourier_transformations(*args, **kwargs):
            power_spectrum = self._scale_fourier(np.absolute(self._scale_fourier(trans)) ** 2)
            if with_freqs:
                yield power_spectrum, np.fft.rfftfreq(self.sample_size, d=self.sample_spacing)
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

