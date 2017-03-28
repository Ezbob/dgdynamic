#!/usr/bin/python
from array import array
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets


def calc_plot(signal_function, bin_size=None, line_width=0.09):
    figure = plt.figure(figsize=(16, 10))
    # sample_space = np.linspace(0, 1, num=sample_size)
    sample_space = np.arange(0.0, 1.0, 0.001)

    signal_data = signal_function(sample_space)

    subplot = figure.add_subplot(2, 1, 1)

    signal_plot, = subplot.plot(sample_space, signal_data)
    #subplot.set_ylim([-10, 10])

    if hasattr(signal_function, "name"):
        subplot.set_title(signal_function.name)
    else:
        subplot.set_title("Signal function")

    fourier = np.fft.fft(signal_data)

    # only calculate the one-sided amplitude spectrum
    spectrum_size = len(fourier) // 2 if bin_size is None else bin_size
    spectrum_range = array('d', range(0, spectrum_size))

    amplitude_spectrum = np.abs(fourier[:spectrum_size])

    amp_subplot = figure.add_subplot(2, 2, 3)

    #amp_subplot.set_xticks(spectrum_range)
    amp_rectangles = amp_subplot.bar(spectrum_range, amplitude_spectrum, line_width)
    amp_subplot.set_title("Amplitude spectrum")

    power_spectrum = np.abs(fourier[:spectrum_size]) ** 2

    power_subplot = figure.add_subplot(2, 2, 4)

    #power_subplot.set_xticks(spectrum_range)
    power_rectangles = power_subplot.bar(spectrum_range, power_spectrum, line_width)
    power_subplot.set_title("Power spectrum")

    return fourier


def interactive_plot(bin_size=None, line_width=0.09):
    """
    Calculates and plots the data, the amplitude spectrum diagram
    and the power spectrum of a signal function
    """

    def signal_function(t): return np.sin(2 * np.pi * t)

    figure = plt.figure(figsize=(16, 10))
    sample_space = np.arange(0.0, 1.0, 0.001)

    signal_data = signal_function(sample_space)

    subplot = figure.add_subplot(2, 1, 1)

    signal_plot, = subplot.plot(sample_space, signal_data)
    subplot.set_ylim([-10, 10])

    subplot.set_title("Signal; $A \cdot e^{2\pi f}$")

    fourier = np.fft.fft(signal_data)

    # only calculate the one-sided amplitude spectrum
    spectrum_size = len(fourier) // 2 if bin_size is None else bin_size
    spectrum_range = array('d', range(0, spectrum_size))

    amplitude_spectrum = np.abs(fourier[:spectrum_size])

    amp_subplot = figure.add_subplot(2, 2, 3)

    amp_rectangles = amp_subplot.bar(spectrum_range, amplitude_spectrum, line_width)
    amp_subplot.set_title("Amplitude spectrum")

    power_spectrum = np.abs(fourier[:spectrum_size]) ** 2

    power_subplot = figure.add_subplot(2, 2, 4)

    power_rectangles = power_subplot.bar(spectrum_range, power_spectrum, line_width)
    power_subplot.set_title("Power spectrum")

    figure.tight_layout()

    plt.subplots_adjust(bottom=0.25)

    axcolor = 'lightgoldenrodyellow'
    axfreq = plt.axes([0.20, 0.1, 0.70, 0.03], axisbg=axcolor)
    axamp = plt.axes([0.20, 0.15, 0.70, 0.03], axisbg=axcolor)

    slider_freq = widgets.Slider(axfreq, '$f$', 0.1, 30.0, valinit=1)
    slider_amp = widgets.Slider(axamp, '$A$', 0.1, 10.0, valinit=1)

    def update(val):
        new_amp = slider_amp.val
        new_freq = slider_freq.val
        new_y_data = new_amp * np.sin(2 * np.pi * new_freq * sample_space)
        new_fourier = np.fft.fft(new_y_data)
        signal_plot.set_ydata(new_y_data)

        new_amp_data = np.abs(new_fourier[:spectrum_size])
        new_pwr_data = new_amp_data ** 2

        for new_height, rectangle in zip(new_amp_data, amp_rectangles):
            rectangle.set_height(new_height)
        for new_height, rectangle in zip(new_pwr_data, power_rectangles):
            rectangle.set_height(new_height)

        amp_subplot.relim()
        amp_subplot.autoscale_view()

        power_subplot.relim()
        power_subplot.autoscale_view()

        figure.canvas.draw_idle()

    slider_freq.on_changed(update)
    slider_amp.on_changed(update)


if __name__ == "__main__":
    # this is just a nice little simple sinus function
    def sinus_function(t): return np.sin(2 * np.pi * t)
    sinus_function.name = "Signal; $\sin(2 \cdot \pi \cdot t)$"

    fourier = calc_plot(sinus_function, 50)


    def sinus_function2(t): return np.sin(6 * np.pi * t)
    sinus_function2.name = "Signal; $\sin(6 \cdot \pi \cdot t)$"

    calc_plot(sinus_function2)

    # def sinus_function3(t): return 0.5 * np.sin(2 * np.pi * t)
    # sinus_function.name = "Signal; sin(2*\pi*t)"

    interactive_plot(100)

    plt.show()
