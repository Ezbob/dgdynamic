"""
Case 2: Continued on the hyper cycle definition from case 1, we here try some direction to each of the hyper cycles.
This means that we take a reaction from each of the hyper cycles and make the backward reaction dependent on a fraction
of the forward reaction. This should add a sense of flow direction to the two hyper cycles.
"""
from dgdynamic import dgDynamicSim, HyperGraph
from dgdynamic.analytics import DynamicAnalysisDevice
from dgdynamic.utils.exceptions import SimulationError
import matplotlib.pyplot as plt
import random
import enum
import csv
import datetime
import os.path
import argparse
import numpy as np
import warnings


def argument_handler():
    """Parses CLI arguments for the script"""
    defaults = {
        'runs': 2,
        'output_dir': "eschenmoser_data/",
        'plugin': 'stochkit2',
        'method': 'tauleaping',
        'plot': False,
        'limit_factor': 0.1
    }
    parser = argparse.ArgumentParser(description="Eschenmoser (Reversible case 2) script. Calculates the measurements.")
    parser.add_argument('-r', '--runs', type=int, help="How many runs does this script need to run",
                        default=defaults['runs'])
    parser.add_argument('-o', '--output_dir', help="Where to dump the output data", default=defaults['output_dir'])
    parser.add_argument('-p', '--plugin', help="Which plugin to use", choices=['scipy', 'matlab', 'stochkit2', 'spim'],
                        default=defaults['plugin'])
    parser.add_argument('-m', '--method', help="Which method to use. Please choose a matching method with plugin",
                        default=defaults['method'])
    parser.add_argument('-s', '--plot', help="Do and save plots in the output directory", default=defaults['plot'],
                        action='store_true')
    parser.add_argument('-l', '--limiter', help="Backward reaction limit factor for the targeted reactions",
                        default=defaults['limit_factor'], type=float, choices=[1., 0.1, 0.01, 0.001, 0.0001, 0.00001])

    parsed_args = parser.parse_args()
    output_dir = os.path.abspath(parsed_args.output_dir)
    return parsed_args.runs, output_dir, parsed_args.plugin, parsed_args.method, parsed_args.plot, parsed_args.limiter

runs, output_dir, plugin_name, method_name, do_plots, backward_limiter = argument_handler()

file_prefix = "eschenmoser_r2"

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

print("Starting on the Eschenmoser(Reversible case 2) script with {} runs and output dir: {}.".format(runs, output_dir))


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

# These are the "targeted" reaction which should add a
targeted_c1_reaction = "C1S5 <=> C1S6 + {}".format(ImportantSpecies.Glyoxylate.name)
targeted_c2_reaction = "C2S3 <=> {} + {}" \
    .format(ImportantSpecies.Oxaloglycolate.name, ImportantSpecies.Oxoaspartate.name)

print("Targeted reactions for cycle 1: {} and cycle2: {}".format(targeted_c1_reaction, targeted_c2_reaction))

cycle1_hyper = HyperGraph.from_abstract(*cycle1_reactions)
cycle2_hyper = HyperGraph.from_abstract(*cycle2_reactions)

reactions = cycle1_reactions + cycle2_reactions
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


def generate_rates(reactions):
    """Generate random rates for reactions"""
    rates = []
    print("Backward reaction limiter set to: {}".format(backward_limiter))
    for reaction in reactions:
        if '<=>' in reaction:
            if reaction in [targeted_c1_reaction, targeted_c2_reaction]:
                f = random.random()
                b = backward_limiter * f
                print("Setting {} to have forward {} and backward {} rates".format(reaction, f, b))
                rates.append(
                    {'->': f, '<-': b}
                )
            else:
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


def add_natural_drain(symbols, natural_drain=0.0001):
    count = 0
    for sym in symbols:
        if sym not in drain_params or 'out' not in drain_params[sym]:

            drain_params[sym] = {
                'out': {
                    'factor': natural_drain
                }
            }
            count += 1
    print("Natural out drain set to {} for {} reactions".format(natural_drain, count))

parameter_matrix = tuple({r: rate_dict for r, rate_dict in zip(reactions, generate_rates(reactions))}
                         for _ in range(runs))

ode = dgDynamicSim(dg)
stochastic = dgDynamicSim(dg, 'stochastic')
add_natural_drain(ode.symbols)

sim_end_time = 60000
period_bounds = (600, sim_end_time / 2)  # looking from 600 to 30000

measurement_output = {
    'variance': [],
    'fourier_amp': [],
    'fourier_freq': [],
    'n_sample': [],
    'end_t': [],
    'pair_diff': []
}


def write_score_data_parameter(name):
    """Write all data to a TSV file"""

    def fp(float_value, fixed_precision=18):
        """Fixed point string format conversion"""
        return "{:.{}f}".format(float_value, fixed_precision)

    def spilt_reversible(r):
        """This splits reversible reaction into forward('->') and backward('->') components"""
        if '<=>' in r:
            prefix, _, suffix = r.partition('<=>')
            return prefix + '->' + suffix, prefix + '<-' + suffix
        return r,

    def count_cycle_params():
        """Get the reaction count for each cycle. A reversible reactions count for two reactions"""
        return sum(2 if '<=>' in r else 1 for r in cycle1_reactions), \
               sum(2 if '<=>' in r else 1 for r in cycle2_reactions)

    def add_header(writer):
        """Calculate the header (first line in tsv file) which determines the order of variables"""
        f_amp_score_labels = ["fourier_amp_" + sym for sym in ode.symbols]
        f_freq_score_labls = ["fourier_freq_" + sym for sym in ode.symbols]
        v_score_labels = ["variance_" + sym for sym in ode.symbols]
        pd_score_labels = ["pair_diff_" + sym for sym in ode.symbols]

        param_labels = []
        for r in reactions:
            splitted = spilt_reversible(r)
            for label in splitted:
                param_labels.append(label)

        assert len(param_labels) == (c1_count + c2_count) == ode.reaction_count
        assert len(f_amp_score_labels) == ode.species_count
        assert len(f_freq_score_labls) == ode.species_count
        assert len(v_score_labels) == ode.species_count

        whole_header = ['species_n', 'c1_param_n', 'c2_param_n', 'sample_n', 'end_t', 'expected_end_t',
                        'lower_period_bound', 'upper_period_bound']
        whole_header += v_score_labels + pd_score_labels + f_amp_score_labels + f_freq_score_labls + param_labels
        writer.writerow(whole_header)
        return len(whole_header)

    dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    file_name = "{}_{}_{}_measurements_{}_{}.tsv".format(file_prefix, name, backward_limiter, runs, dt)
    file_path = os.path.join(output_dir, file_name)
    print("Output file:\n{}".format(file_path))

    with open(file_path, mode="w") as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter="\t")
        c1_count, c2_count = count_cycle_params()

        header_length = add_header(tsv_writer)

        for i, param_map in enumerate(parameter_matrix):
            param_list = []
            for r in reactions:
                rate_dict = param_map[r]
                param_list.append(fp(rate_dict['->']))
                if '<-' in rate_dict:
                    param_list.append(fp(rate_dict['<-']))

            assert ode.reaction_count == (c1_count + c2_count), "Not enough reactions"
            assert len(param_list) == (c1_count + c2_count), "Not enough parameters"
            assert len(measurement_output['fourier_amp'][i]) == ode.species_count, "Not enough amplitude measures"
            assert len(measurement_output['variance'][i]) == ode.species_count, "Not enough variances measures"
            assert len(measurement_output['pair_diff'][i]) == ode.species_count, "Not enough pair diff measures"

            data_row = [ode.species_count, c1_count, c2_count, measurement_output['n_sample'][i],
                        measurement_output['end_t'][i], sim_end_time, fp(period_bounds[0]), fp(period_bounds[1])]
            for label in ['variance', 'pair_diff', 'fourier_amp', 'fourier_freq']:
                data_row += list(map(fp, measurement_output[label][i]))
            data_row += param_list

            assert len(data_row) == header_length, "Header length and data row length differs"
            tsv_writer.writerow(data_row)


def do_sim_and_measure(run_number, params, plugin, plugin_name, method, do_plot=False):
    """Do a simulation run and get the measurements"""
    plugin.method = method

    if hasattr(plugin, "delta_t"):
        # For most ODEs we have delta
        plugin.delta_t = 1
    else:
        # For stochastic sim we set the resolution (that is the number of sample numbers needed)
        plugin.resolution = sim_end_time

    out = plugin(sim_end_time, initial_conditions, params, drain_params)

    assert out is not None, "Output from run {} was None".format(run_number)

    if out.has_errors and len(out.dependent) == len(out.independent) == 0:
        warnings.warn("Simulation Error encountered using plugin: {}".format(plugin_name))
        raise SimulationError(*[m for err in out.errors for m in err.args])

    analytics = DynamicAnalysisDevice(out)
    sim_end = out.independent[-1]
    n_sample_points = len(out.dependent)

    print("Is data equally spaced?", out.is_data_evenly_spaced())
    print("Stop prematurely?", out.has_sim_prematurely_stopped())

    if not out.is_data_evenly_spaced():
        print("Data was not equally spaced. Applying linear interpolation...")
        out = out.interpolate_data(new_sample_resolution=sim_end_time)

    freqs = analytics.fourier_frequencies
    amp_spec = analytics.amplitude_spectra

    print("Frequency bins: {}".format(len(freqs)))
    freqs, amp_spec = analytics.cutoff_dc_component(freqs, amp_spec)

    variance_measurement = np.array([data.var() for data in out.dependent.T])
    print("Variance measurements: {}".format(variance_measurement))
    pair_diff = analytics.pair_distance_measurement()
    print("Pair distance measurements: {}".format(pair_diff))
    fourier_amplitude_measurement = np.array([], dtype=float)
    fourier_frequency_measurement = np.array([], dtype=float)

    for i in range(ode.species_count):
        arg_max_fourier = amp_spec[i].argmax()
        fourier_amplitude_measurement = np.append(fourier_amplitude_measurement, amp_spec[i, arg_max_fourier])
        fourier_frequency_measurement = np.append(fourier_frequency_measurement, freqs[arg_max_fourier])

    assert len(fourier_amplitude_measurement) == len(fourier_frequency_measurement)
    assert len(fourier_amplitude_measurement) == len(variance_measurement)
    print("Fourier maximum amplitude measurements: {}".format(fourier_amplitude_measurement))
    print("Fourier maximum frequency measurements: {}".format(fourier_frequency_measurement))

    if do_plot and not out.has_sim_prematurely_stopped():
        dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
        title = "{} {} limiter {} - Run: {} / {}, measures: (std-dev: {}, amp: {}, freq: {}, pd: {})"\
            .format(out.solver_used.name, method, backward_limiter, run_number + 1, runs,
                    max(np.sqrt(variance_measurement)), max(fourier_amplitude_measurement),
                    max(fourier_frequency_measurement), max(pair_diff))

        image_path = os.path.join(output_dir, "{}_{}_{}_plot{}_{}_{}.png"
                                  .format(file_prefix, plugin_name, method_name, run_number + 1, runs, dt))
        out.plot(filename=image_path, figure_size=(46, 24), title=title)

        image_path = os.path.join(output_dir, "{}_fourier_{}_{}_plot{}_{}_{}.png"
                                  .format(file_prefix, plugin_name, method_name, run_number + 1, runs, dt))
        analytics.plot_spectra(amp_spec, freqs, title=title, filename=image_path, figure_size=(46, 24))
        plt.close('all')  # we don't need to show the figures

    if out.has_sim_prematurely_stopped():
        dt = "{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
        title = "{} {} - Run: {} / {}, measures: (std-dev: {}, amp: {}, freq: {}, pair_diff: {}), aborted at ({}, {})" \
            .format(out.solver_used.name, method, run_number + 1, runs, max(np.sqrt(variance_measurement)),
                    max(fourier_amplitude_measurement), max(fourier_frequency_measurement),
                    max(pair_diff), out.independent[-1], out.dependent[-1])

        image_path = os.path.join(output_dir, "aborted_{}_{}_{}_plot{}_{}_{}.png".format(
            file_prefix, plugin_name, method_name, run_number + 1, runs, dt))
        out.plot(filename=image_path, figure_size=(46, 24), title=title)
        plt.close('all')

    measurement_output['n_sample'].append(n_sample_points)
    measurement_output['end_t'].append(sim_end)
    measurement_output['variance'].append(variance_measurement)
    measurement_output['fourier_freq'].append(fourier_frequency_measurement)
    measurement_output['fourier_amp'].append(fourier_amplitude_measurement)
    measurement_output['pair_diff'].append(pair_diff)


def main():
    """Do the actual simulation"""

    plugins = {
        'matlab': ode('matlab'),
        'scipy': ode('scipy'),
        'stochkit2': stochastic('stochkit2'),
        'spim': stochastic("spim")
    }
    try:
        for index, parm in enumerate(parameter_matrix):
            print("--- Run {} ---".format(index + 1))

            #  FIXME fourier for matlab is exceedingly slow
            #  TODO find out why spim is slacking

            do_sim_and_measure(index, parm, plugins[plugin_name], plugin_name, method_name, do_plot=do_plots)

    except KeyboardInterrupt:
        print("Received Interrupt Signal. ")
    except SimulationError as e:
        print("Received Simulation error: ", *e.args)
    finally:
        print("Writing results to output file..")
        write_score_data_parameter(plugin_name)

if __name__ == '__main__':
    main()

