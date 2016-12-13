import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from dgDynamic.output import SimulationOutput


class DynamicAnalysisDevice:
    def __init__(self, simulation_output: SimulationOutput, sample_spacing=None, plugin_solver=None,
                 sample_rate=None, windowing_function=None):
        self.output = simulation_output
        self.solver_plugin = plugin_solver
        self.windowing_function = windowing_function
        self.sample_size = len(self.output.dependent)
        # default: assuming uniform spacing between time samples
        self.sample_rate = self.sample_size / self.output.simulation_duration \
            if sample_rate is None else sample_rate
        self.sample_spacing = 1 / self.sample_rate if sample_spacing is None else sample_spacing

    @staticmethod
    def from_simulation(plugin, simulation_range, initial_conditions, rate_parameters,
                        drain_parameters=None, using_filtered_output=True, *args, **kwargs):
        if using_filtered_output:
            output = plugin(simulation_range, initial_conditions, rate_parameters,
                            drain_parameters, *args, **kwargs).filtered_output
        else:
            output = plugin(simulation_range, initial_conditions, rate_parameters,
                            drain_parameters, *args, **kwargs)

        sample_spacing = None
        sample_rate = None
        if hasattr(plugin, "delta_t"):
            sample_spacing = plugin.delta_t
            sample_rate = output.requested_simulation_range[1] * sample_spacing

        return output, DynamicAnalysisDevice(output, plugin_solver=plugin, sample_rate=sample_rate,
                                             sample_spacing=sample_spacing)

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
                yield power_spectrum, self.fourier_frequencies
            else:
                yield power_spectrum

    def nonzero_maxima(self, data, frequencies=None):
        arg_maxima = np.trim_zeros(signal.argrelmax(data=data, mode="wrap")[0])
        maxima = np.fromiter((data[i] for i in arg_maxima), dtype=float)
        freqs = self.fourier_frequencies if frequencies is None else frequencies
        return maxima, np.fromiter((freqs[i] for i in arg_maxima), dtype=float)

    def nonzero_maximum(self, data, frequencies=None):
        maxima, maxima_freqs = self.nonzero_maxima(data, frequencies)
        try:
            arg_maximum = np.argmax(maxima)
            return maxima[arg_maximum], maxima_freqs[arg_maximum]
        except ValueError:
            return np.nan, np.nan

    @property
    def fourier_frequencies(self):
        return np.fft.rfftfreq(self.sample_size, d=self.sample_spacing)

    @property
    def amplitude_spectra(self):
        return tuple(self.generate_amplitude_spectrum())

    @property
    def power_spectra(self):
        return tuple(self.generate_power_spectrum())

    def power_spectrum(self, index):
        return tuple(self.generate_power_spectrum())[index]

    def amplitude_spectrum(self, index):
        return tuple(self.generate_amplitude_spectrum())[index]

    def plot_spectra(self, spectra_data, frequencies, include_maxima=False, include_maximum=False,
                     is_power_spectra=False):
        plt.figure()
        plt.grid()
        for data, label in zip(spectra_data, self.output.symbols):
            if is_power_spectra:
                plt.ylabel("power")
            else:
                plt.ylabel("amplitude")
            plt.xlabel("frequencies")
            plt.plot(frequencies, data, marker='o', label=label)

            if include_maxima:
                maxima_values, maxima_frequency = self.nonzero_maxima(data, frequencies)
                plt.plot(maxima_frequency, maxima_values, 'ro', color='white')
            if include_maximum:
                maximum_value, maximum_frequency = self.nonzero_maximum(data, frequencies)
                plt.plot(maximum_frequency, maximum_value, 'ro', marker='+', color='black')

        plt.legend()
