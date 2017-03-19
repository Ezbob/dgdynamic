from dgDynamic import dgDynamicSim, HyperGraph
import matplotlib.pyplot as plt
from dgDynamic.analytics import DynamicAnalysisDevice
import random
import enum
import csv
import datetime
import os.path
import argparse
import numpy as np


def argument_handler():
    defaults = {
        'runs': 2,
        'output_dir': "eschenmoser_data/",
        'plugin': 'stochkit2',
        'method': 'tauleaping'
    }
    parser = argparse.ArgumentParser(description="Eschenmoser (reversible) script. Calculates the measurements.")
    parser.add_argument('-r', '--runs', type=int, help="How many runs does this script need to run",
                        default=defaults['runs'])
    parser.add_argument('-o', '--output_dir', help="Where to dump the output data", default=defaults['output_dir'])
    parser.add_argument('-p', '--plugin', help="Which plugin to use", choices=['scipy', 'matlab', 'stochkit2', 'spim'],
                        default=defaults['plugin'])
    parser.add_argument('-m', '--method', help="Which method to use. Please choose a matching method with plugin",
                        default=defaults['method'])

    parsed_args = parser.parse_args()
    output_dir = os.path.abspath(parsed_args.output_dir)
    return parsed_args.runs, output_dir, parsed_args.plugin, parsed_args.method

runs, output_dir, plugin_name, method_name = argument_handler()

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

print("Starting on the Eschenmoser(Reversible) script with {} runs and output dir: {}.".format(runs, output_dir))


class ImportantSpecies(enum.Enum):
    HCN = "HCN"
    Glyoxylate = "Glyoxylate"
    Oxaloglycolate = "Oxaloglycolate"
    Oxoaspartate = "Oxoaspartate"


cycle1_reactions = [
    "2 {} <=> C1S1".format(ImportantSpecies.HCN.name),
    "C1S1 <=> C1S2",
    "C1S2 + {} <=> C1S3".format(ImportantSpecies.Glyoxylate.name),
    "C1S3 <=> C1S4",
    "C1S4 <=> C1S5",
    "C1S5 <=> C1S6 + {}".format(ImportantSpecies.Glyoxylate.name),
    "C1S6 <=> {}".format(ImportantSpecies.Glyoxylate.name),
]

cycle2_reactions = [
    "C2S10 + {} <=> C2S1".format(ImportantSpecies.Glyoxylate.name),
    "C2S1 <=> C2S2",
    "C2S2 <=> C2S3",
    "C2S3 <=> {} + {}".format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.Oxoaspartate.name),
    "{} <=> C2S4".format(ImportantSpecies.Oxaloglycolate.name),
    "C2S4 <=> C2S5",
    "C2S5 <=> C2S6",
    "{} <=> C2S6".format(ImportantSpecies.Oxoaspartate.name),
    "{} + C2S6 <=> C2S7".format(ImportantSpecies.Glyoxylate.name),
    "C2S7 <=> C2S8",
    "C2S8 <=> C2S9",
    "C2S9 <=> C2S10"
]

cycle1_hyper = HyperGraph.from_abstract(*cycle1_reactions)
cycle2_hyper = HyperGraph.from_abstract(*cycle2_reactions)

#  cycle1_hyper.print()
#  cycle2_hyper.print()

reactions = cycle1_reactions + cycle2_reactions


def generate_rates(reactions):
    """Get a list of tuples containing the random rates"""
    rates = []
    for reaction in reactions:
        if '<=>' in reaction:
            f = random.random()
            b = random.random()
            rates.append(
                {'->': f, '<-': b}
            )
        else:
            f = random.random()
            rates.append(
                {'->': f}
            )
    return rates


def fp(float_value, fixed_precision=18):
    """Fixed point string format conversion"""
    return "{:.{}f}".format(float_value, fixed_precision)


def write_score_data_parameter(name):

    def spilt_reversible(r):
        if '<=>' in r:
            prefix, _, suffix = r.partition('<=>')
            return prefix + '->' + suffix, prefix + '<-' + suffix
        return r,

    def count_cycle_params():
        return sum(2 if '<=>' in r else 1 for r in cycle1_reactions), \
               sum(2 if '<=>' in r else 1 for r in cycle2_reactions)

    dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    file_name = "eschenmoser_r_{}_measurements_{}_{}.tsv".format(name, runs, dt)
    file_path = os.path.join(output_dir, file_name)
    print("Output file: {}".format(file_path))
    with open(file_path, mode="w") as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter="\t")
        c1_count, c2_count = count_cycle_params()

        f_score_labels = ["fourier_" + sym for sym in ode.symbols]
        v_score_labels = ["variance_" + sym for sym in ode.symbols]

        param_labels = []
        for r in reactions:
            splitted = spilt_reversible(r)
            for label in splitted:
                param_labels.append(label)

        assert len(param_labels) == (c1_count + c2_count) == ode.reaction_count
        assert len(f_score_labels) == ode.species_count
        assert len(v_score_labels) == ode.species_count
        tsv_writer.writerow(['species_n', 'c1_param_n', 'c2_param_n', 'lower_period_bound', 'upper_period_bound']
                            + f_score_labels
                            + v_score_labels
                            + param_labels)

        for var_measure, fourier_measure, param_map in zip(variance_measurements, fourier_measurements,
                                                           parameter_matrix):
            param_list = []
            for r in reactions:
                rate_dict = param_map[r]
                param_list.append(rate_dict['->'])
                if '<-' in rate_dict:
                    param_list.append(rate_dict['<-'])

            assert ode.reaction_count == (c1_count + c2_count)
            assert len(param_list) == (c1_count + c2_count), "Not enough parameters"
            assert len(fourier_measure) == ode.species_count, "At least one fourier measure"
            assert len(var_measure) == ode.species_count
            row = [ode.species_count, c1_count, c2_count, fp(period_bounds[0]), fp(period_bounds[1])] \
                + [fp(measure) for measure in fourier_measure] \
                + [fp(measure) for measure in var_measure] \
                + param_list
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

parameter_matrix = tuple({r: rate_dict for r, rate_dict in zip(reactions, generate_rates(reactions))}
                         for _ in range(runs))
#  dg.print()

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

fourier_measurements = []
variance_measurements = []

plugins = {
    'matlab': ode('matlab'),
    'scipy': ode('scipy'),
    'stochkit2': stochastic('stochkit2'),
    'spim': stochastic("spim")
}


def do_sim_and_measure(run_number, params, plugin, plugin_name, method, do_plot=False):
    """Run some simulation and get the measurements"""
    print("Using plugin: {}".format(plugin_name))
    if hasattr(plugin, "method"):
        # caveat #1: Not all plugins have a method (e.g.: the SPiM plugin only works with it's default method)
        plugin.method = method

    # caveat #2: the simulation_range format is different when using ODEs and stochastic methods
    # stochastic methods assume that the the start time of the sim is zero, and includes some resolution count (e.g.
    # how many sample do we need over the sim period)
    sim_range = ode_sim_range if plugin_name.lower() in ['scipy', 'matlab'] else stoch_sim_range

    out = plugin(sim_range, initial_conditions, params, drain_params)
    if out.is_output_set:
        # caveat #3: the stochkit2 returns SimulationOutputSet which are collections of SimulationOutput.
        # This is to handle the outputting of multiple trajectories/random walks/realizations
        out = out[0]
    if out.has_errors and len(out.dependent) == len(out.independent) == 0:
        print("Error in simulating {}".format(plugin_name))
        for err in out.errors:
            print(err)
        return None
    analytics = DynamicAnalysisDevice(out)
    variance_measurement = np.array([data.var() for data in out.dependent.T])
    print("Variance measurements: {}".format(variance_measurement))
    amp_spec = analytics.amplitude_spectra
    freqs = analytics.fourier_frequencies
    fourier_measurement = np.array([
        analytics.bounded_fourier_oscillation(amp_spec, i, period_bounds[0], period_bounds[1], freqs)
        for i in range(ode.species_count)
    ])
    #  analytics.fourier_oscillation_measure(period_bounds[0], period_bounds[1])
    print("Fourier oscillation measurements: {}".format(fourier_measurement))

    if do_plot:
        dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
        title = "{} {} - Run: {} / {}, var: {}, four: {}"\
            .format(out.solver_used.name, method, run_number + 1, runs, max(variance_measurement), max(fourier_measurement))

        image_path = os.path.join(output_dir, "eschenmoser_{}_{}_plot{}_{}_{}.png".format(plugin_name, method_name,
                                                                                          run_number + 1, runs, dt))
        out.plot(filename=image_path, figure_size=(46, 24), title=title)
    return variance_measurement, fourier_measurement


def find_minimum_reaction_rates(param):
    cycle1_forward_params = [param[k]['->'] for k in cycle1_reactions]
    cycle1_backward_params = [param[k]['<-'] for k in cycle1_reactions]
    cycle2_forward_params = [param[k]['->'] for k in cycle2_reactions]
    cycle2_backward_params = [param[k]['<-'] for k in cycle2_reactions]

    c1_minimal_rates = min(cycle1_forward_params), min(cycle1_backward_params)
    c2_minimal_rates = min(cycle2_forward_params), min(cycle2_backward_params)

    if c1_minimal_rates[0] < c1_minimal_rates[1]:
        fm = c1_minimal_rates[0]
        fr = cycle1_reactions[cycle1_forward_params.index(fm)].replace('<=>', '->')
    else:
        fm = c1_minimal_rates[1]
        fr = cycle1_reactions[cycle1_backward_params.index(fm)].replace('<=>', '<-')

    if c2_minimal_rates[0] < c2_minimal_rates[1]:
        bm = c2_minimal_rates[0]
        br = cycle2_reactions[cycle2_forward_params.index(bm)].replace('<=>', '->')
    else:
        bm = c2_minimal_rates[1]
        br = cycle2_reactions[cycle2_backward_params.index(bm)].replace('<=>', '<-')

    print("Cycle 1 reaction {!r} with minimal rate: {}".format(fr, fm))
    print("Cycle 2 reaction {!r} with minimal rate: {}".format(br, bm))


def main():
    """Do the actual simulation"""
    try:
        for index, parm in enumerate(parameter_matrix):
            print("--- Run {} ---".format(index + 1))
            find_minimum_reaction_rates(parm)

            #  FIXME fourier for matlab is exceedingly slow
            #  TODO find out why spim is slacking
            var_mes, four_mes = do_sim_and_measure(index, parm, plugins[plugin_name], plugin_name, method_name,
                                                   do_plot=True)

            variance_measurements.append(var_mes)
            fourier_measurements.append(four_mes)

    except KeyboardInterrupt:
        print("Received Interrupt Signal. ")
        print("Writing results to output file..")
        write_score_data_parameter(plugin_name)

    print("Writing results to output file..")
    write_score_data_parameter(plugin_name)


if __name__ == '__main__':
    main()
    #  print(tuple(ode.symbols))
    #  pass

#show_plots()
