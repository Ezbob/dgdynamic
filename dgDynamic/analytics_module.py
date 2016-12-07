import numpy as np
import scipy.signal as signal
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

    def generate_amplitude_spectrum(self, with_frequencies=False, *args, **kwargs):
        for fourier_trans in self.generate_fourier_transformations(*args, **kwargs):
            amplitudes = self._scale_fourier(np.absolute(fourier_trans))
            if with_frequencies:
                yield amplitudes, np.fft.rfftfreq(self.sample_size, d=self.sample_spacing)
            else:
                yield amplitudes

    def generate_power_spectrum(self, with_frequencies=False, *args, **kwargs):
        for trans in self.generate_fourier_transformations(*args, **kwargs):
            power_spectrum = self._scale_fourier(np.absolute(self._scale_fourier(trans)) ** 2)
            if with_frequencies:
                yield power_spectrum, self.frequencies
            else:
                yield power_spectrum

    def nonzero_maxima(self, data, frequencies=None):
        arg_maxima = tuple(m for m in signal.argrelmax(data=data, mode="wrap")[0] if m > 0)
        maxima = np.fromiter((data[i] for i in arg_maxima), dtype=float)
        frequencies = self.frequencies if frequencies is None else frequencies
        return maxima, np.fromiter((frequencies[i] for i in arg_maxima), dtype=float)

    def nonzero_maximum(self, data, frequencies=None):
        maxima, maxima_frequencies = self.nonzero_maxima(data, frequencies)
        arg_maximum = np.argmax(maxima)
        return maxima_frequencies[arg_maximum], maxima[arg_maximum]

    @property
    def frequencies(self):
        return np.fft.rfftfreq(self.sample_size, d=self.sample_spacing)

    def power_spectrum(self, index):
        return tuple(self.generate_power_spectrum())[index]

    def amplitude_spectrum(self, index):
        return tuple(self.generate_amplitude_spectrum())[index]
