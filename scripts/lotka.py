"""
A Lotka-Volterra model with (F)oxes and (R)abbits (prey-predator model).
    Rabbits eat grass and multiples
    Foxes hunt and eat rabbits and multiples
    Foxes also dies of old age
"""
from dgDynamic import dgDynamicSim, show_plots, HyperGraph, DynamicAnalysisDevice

rabbit_multiples = "R -> 2 R"
foxes_hunts = "R + F -> F + F"

dg = HyperGraph.from_abstract(rabbit_multiples, foxes_hunts,)

initial_conditions = {
    'F': 250,
    'R': 250
}

parameters = {
    foxes_hunts: 0.005,
    rabbit_multiples: 0.7,
}

drain_parameters = {
    'F': {
        'out': {
            'factor': 0.5
        }
    }
}

integration_range = (0, 100)

ode = dgDynamicSim(dg, simulator_choice='ode')
stochastic = dgDynamicSim(dg, simulator_choice='stochastic')

# Name of the data set
name = "foxesRabbits"
figure_size = (40, 20)

scipy = ode('scipy')
matlab = ode('matlab')

# Run the simulation and give us the output and the analytic class
# which gives access to computation of the Fourier transformation etc..
# The output can be inspected and plotted like a normal output class
output, analytics = DynamicAnalysisDevice.from_simulation(scipy, integration_range, initial_conditions,
                                      parameters, drain_parameters)

# Plotting the simulation output
output.plot(figure_size=figure_size)

# Get the domain values for the Fourier
fourier_freqs = analytics.fourier_frequencies

# Plot the amplitude spectra (all of them)
analytics.plot_spectra(analytics.amplitude_spectra, fourier_freqs)

# Plot the power spectra
analytics.plot_spectra(analytics.power_spectra, fourier_freqs, is_power_spectra=True)

# /-------  /-----\  -------\ #
# *---- SPiM Simulation ----* #
# \-------  \-----/  -------/ #

# Set the new SPiM simulation, first number is maximum simulation,
# second number is the number of data points needed
spim_simulation_range = (100, 1000)

with stochastic('spim') as spim:
    spim.timeout = 2
    for _ in range(4):
        output, analytics = DynamicAnalysisDevice.from_simulation(spim,
                                                                  simulation_range=spim_simulation_range,
                                                                  initial_conditions=initial_conditions,
                                                                  rate_parameters=parameters,
                                                                  drain_parameters=drain_parameters)
        # The time domain plot comes before the frequency plot
        output.plot(figure_size=figure_size)

        analytics.plot_spectra(analytics.amplitude_spectra, analytics.fourier_frequencies,
                               include_maxima=True, include_maximum=True)

# /-------  /----------\  -------\ #
# *---- StochKit2 Simulation ----* #
# \-------  \----------/  -------/ #

# get the plugin
stochkit2 = stochastic('stochkit2')

# the timeout field is a timeout for all trajectories
stochkit2.timeout = 20 * 4

# instead of a for-loop set the number of trajectories as field
stochkit2.trajectories = 4

# the simulate method (which is indirectly accessed here) gives a set of output.
# This set can still be plotted or saved
stochkit2(spim_simulation_range, initial_conditions, parameters, drain_parameters).plot()

# Show all the plots generated so far
show_plots()
