from dgDynamic import dgDynamicSim, HyperGraph, show_plots, choices
import matplotlib.pyplot as plt
from dgDynamic.analytics import DynamicAnalysisDevice
import random
import enum
import csv
import datetime
import sys


runs = int(sys.argv[1]) if len(sys.argv) >= 2 else 2

print("Starting on the Eschenmoser script with {} runs.".format(runs))


class ImportantSpecies(enum.Enum):
    HCN = "HCN"
    Glyoxylate = "Glyoxylate"
    Oxaloglycolate = "Oxaloglycolate"
    Oxoaspartate = "Oxoaspartate"


cycle1_reactions = [
    "2 {} -> C1S1".format(ImportantSpecies.HCN.name),
    "C1S1 -> C1S2",
    "C1S2 + {} -> C1S3".format(ImportantSpecies.Glyoxylate.name),
    "C1S3 -> C1S4",
    "C1S4 -> C1S5",
    "C1S5 -> C1S6 + {}".format(ImportantSpecies.Glyoxylate.name),
    "C1S6 -> {}".format(ImportantSpecies.Glyoxylate.name),
]

cycle2_reactions = [
    "C2S10 + {} -> C2S1".format(ImportantSpecies.Glyoxylate.name),
    "C2S1 -> C2S2",
    "C2S2 -> C2S3",
    "C2S3 -> {} + {}".format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.Oxoaspartate.name),
    "{} <=> C2S4".format(ImportantSpecies.Oxaloglycolate.name),
    "C2S4 <=> C2S5",
    "C2S5 <=> C2S6",
    "{} -> C2S6".format(ImportantSpecies.Oxoaspartate.name),
    "{} + C2S6 -> C2S7".format(ImportantSpecies.Glyoxylate.name),
    "C2S7 -> C2S8",
    "C2S8 -> C2S9",
    "C2S9 -> C2S10"
]

extras = [
    '{} -> {}'.format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.HCN.name)
]

cycle1_hyper = HyperGraph.from_abstract(*cycle1_reactions)
cycle2_hyper = HyperGraph.from_abstract(*cycle2_reactions)

cycle1_hyper.print()
cycle2_hyper.print()

reactions = cycle1_reactions + cycle2_reactions  #+ extras


def generate_rates(number_of_reactions, decomposed_rates=()):
    results = [0.0] * number_of_reactions
    decomposed_args = []

    for decompose_set in decomposed_rates:
        # decomposition of "chain reactions" into elementary reactions yields probability k / p where p
        # are the number reactions that the decomposition yields
        rand = random.random() / len(decompose_set)
        for arg in decompose_set:
            results[arg] = rand
            decomposed_args.append(arg)

    for i in range(number_of_reactions):
        if i not in decomposed_args:
            results[i] = random.random()
    return results


def fp(float_value, fixed_precision=18):
    """Fixed point string format conversion"""
    return "{:.{}f}".format(float_value, fixed_precision)


def write_score_data_parameter(name):
    dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    file_path = "eschenmoser_data/eschenmoser_{}_measurements_{}_{}.tsv".format(name, runs, dt)
    print("Output file: {}".format(file_path))
    with open(file_path, mode="w") as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter="\t")
        tsv_writer.writerow(['c1_param_n', 'c2_param_n', 'variance_sum', 'fourier_score',
                             'lower_period_bound', 'upper_period_bound'] +
                            ['{!r}'.format(r) for r in reactions])
        for var_measure, fourier_measure, param_map in zip(variance_measurements, fourier_measurements, parameter_matrix):
            row = [len(cycle1_reactions), len(cycle2_reactions), fp(var_measure), fp(fourier_measure),
                   fp(period_bounds[0]), fp(period_bounds[1])] + [fp(param_map[r]) for r in reactions]
            tsv_writer.writerow(row)


def print_params(params):
    print("Parameters are: {")
    for react, param in params.items():
        print("{!r}: {},".format(react, param))
    print("}")


def spectrum_plot(analytics, frequency, spectra, period_bounds):
    """Plot a bounded fourier spectrum according to the period bounds"""
    lower_bound, upper_bound = analytics.period_bounds(frequency, period_bounds[0], period_bounds[1])
    analytics.plot_spectra([spect[lower_bound: upper_bound] for spect in spectra],
        frequency[lower_bound: upper_bound])


def plot_minimal_rate_params(cycle1_min_rates, cycle2_min_rates, oscill_measurements):
    """Plots a colored scatter plot, with the colors representing the value of the oscillation measure"""
    plt.figure()
    colormap = plt.cm.get_cmap('RdYlBu')
    plt.grid()

    scatter = plt.scatter(cycle1_min_rates, cycle2_min_rates, c=oscill_measurements, cmap=colormap)

    plt.ylabel("cycle 2 minimal rate")
    plt.xlabel("cycle 1 minimal rate")
    plt.colorbar(scatter)


dg = HyperGraph.from_abstract(*reactions)
all_rates = generate_rates(len(reactions))

initial_conditions = {
    ImportantSpecies.HCN.name: 2,
    ImportantSpecies.Glyoxylate.name: 2,
    ImportantSpecies.Oxaloglycolate.name: 1,
}

drain_params = {
    ImportantSpecies.HCN.name: {
        'in': {
            'constant': 0.1
        },
        'out': {
            'factor': 0.0001
        }
    },
    ImportantSpecies.Glyoxylate.name: {
        'in': {
            'constant': 0.002
        },
        'out': {
            'factor': 0.0001
        }
    },
    ImportantSpecies.Oxaloglycolate.name: {
        'out': {
            'factor': 0.002
        }
    }
}

parameter_matrix = tuple({r: random.random() for r in reactions} for _ in range(runs))

dg.print()

ode = dgDynamicSim(dg)
stochastic = dgDynamicSim(dg, 'stochastic')

for sym in ode.symbols:
    if sym not in drain_params:
        drain_params[sym] = {'out': {
            'factor': 0.0001
        }}

stoch_sim_range = (60000, 3000)
ode_sim_range = (0, 60000)
period_bounds = (600, stoch_sim_range[0] / 2)  # looking from 600 to 30000

c1_minimal_values = []
c2_minimal_values = []
fourier_measurements = []
variance_measurements = []

matlab = ode('matlab')
scipy = ode('scipy')
stochkit2 = stochastic('stochkit2')
spim = stochastic("spim")


def do_sim_and_measure(plugin, plugin_name, method, do_plot=False):
    print("Using plugin: {}".format(plugin_name))
    if hasattr(plugin, "method"):
        plugin.method = method

    sim_range = ode_sim_range if plugin_name.lower() in ['scipy', 'matlab'] else stoch_sim_range

    out = plugin(sim_range, initial_conditions, parm, drain_params)
    if out.is_output_set:
        # for stochkit2 plugin returns output sets for handling multiple trajectories
        out = out[0]
    if out.has_errors and len(out.dependent) == len(out.independent) == 0:
        print("Error in simulating {}".format(plugin_name))
        for err in out.errors:
            print(err)
        return None
    analytics = DynamicAnalysisDevice(out)
    variance_measurement = analytics.variance_oscillation_measure()
    print("Sum variance measurement: {}".format(variance_measurement))
    fourier_measurement = analytics.fourier_oscillation_measure(period_bounds[0], period_bounds[1])
    print("Fourier oscillation measurement: {}".format(fourier_measurement))

    if do_plot:
        dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
        title = "{} {} - Run: {} / {}, var: {}, four: {}"\
            .format(out.solver_used.name, method, index + 1, runs, variance_measurement, fourier_measurement)

        out.plot(filename="eschenmoser_data/eschenmoser_plot{}_{}_{}.png".format(index + 1, runs, dt),
                 figure_size=(46, 24), title=title)
    return variance_measurement, fourier_measurement

try:
    for index, parm in enumerate(parameter_matrix):
        print("--- Run {} ---".format(index + 1))
        cycle1_params = [parm[k] for k in cycle1_reactions]
        cycle2_params = [parm[k] for k in cycle2_reactions]

        cycle1_minimal_rate = min(cycle1_params)
        cycle2_minimal_rate = min(cycle2_params)

        c1_minimal_values.append(cycle1_minimal_rate)
        c2_minimal_values.append(cycle2_minimal_rate)

        print("Cycle 1 reaction {!r} with minimal rate: {}"
              .format(cycle1_reactions[cycle1_params.index(cycle1_minimal_rate)], cycle1_minimal_rate))
        print("Cycle 2 reaction {!r} with minimal rate: {}"
              .format(cycle2_reactions[cycle2_params.index(cycle2_minimal_rate)], cycle2_minimal_rate))

        var_mes, four_mes = do_sim_and_measure(scipy, "scipy", "LSODA")
        variance_measurements.append(var_mes)
        fourier_measurements.append(four_mes)

        # do_sim_and_measure(stochkit2, "stochkit2", "tauleaping")
        # do_sim_and_measure(matlab, "matlab", "ode45", do_plot=True)  # FIXME fourier for matlab is exceedingly slow
        # do_sim_and_measure(spim, "spim", '', do_plot=True)  # TODO find out why spim is slacking

except KeyboardInterrupt:
    print("Received Interrupt Signal. ")
finally:
    print("Writing results to output file..")
    write_score_data_parameter('scipy')

#plot_minimal_rate_params(c1_minimal_values, c2_minimal_values, variance_measurements)

#write_score_data_parameter('scipy')

#show_plots()
