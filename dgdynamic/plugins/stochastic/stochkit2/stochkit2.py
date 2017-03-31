from dgdynamic.plugins.stochastic.stochastic_plugin import StochasticPlugin
from dgdynamic.choices import SupportedStochasticPlugins, StochKit2StochasticSolvers
from .stochkit2_converter import generate_model
from dgdynamic.output import SimulationOutput, SimulationOutputSet
from dgdynamic.plugins.sim_validation import simulation_parameter_validate
import enum
import subprocess
import re
import os
import signal
import array
import tempfile
import dgdynamic.utils.messages as messages
import dgdynamic.config.settings as settings
import os.path as path
import dgdynamic.utils.exceptions as util_exceptions

name = SupportedStochasticPlugins.StochKit2
this_dir = path.abspath(path.dirname(__file__))


class StochKit2Stochastic(StochasticPlugin):

    def __init__(self, simulator, stochastic_method=StochKit2StochasticSolvers.SSA, timeout=None, trajectories=1,
                 resolution=1000):
        super().__init__(simulator, timeout, resolution)
        self._method = stochastic_method
        self.tau_leaping_epsilon = 0.03
        self.switch_threshold = 10
        self._trajectories = abs(int(trajectories))
        self.stochkit2_path = settings.config.get('Simulation', 'STOCHKIT2_PATH', fallback='')
        if self.stochkit2_path == '':
            self.stochkit2_path = path.join(this_dir, 'StochKit')
        else:
            self.stochkit2_path = path.abspath(self.stochkit2_path)

    def model(self, initial_conditions, rate_parameters, drain_parameters=None):
        return generate_model(self._simulator, initial_conditions, rate_parameters, drain_parameters)

    @property
    def method(self):
        if isinstance(self._method, enum.Enum):
            return self._method
        elif isinstance(self._method, str):
            for supported in StochKit2StochasticSolvers:
                name, value = supported.name.lower().strip(), supported.value.lower().strip()
                user_method = self._method.lower().strip()
                if user_method == name or user_method == value:
                    return supported

    @property
    def flag_options(self):
        flags = ['--no-stats', '--keep-trajectories', '--label', '-f']
        return flags

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def trajectories(self):
        return self._trajectories

    @trajectories.setter
    def trajectories(self, value):
        self._trajectories = abs(int(value))

    def simulate(self, end_t, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        model_filename = "model.xml"
        output_dirname = "model_output"
        self.logger.info("Starting on StochKit2 simulation with {} trajectories, "
                         "{} method, end time: {}, and {} sample points".format(self.trajectories, self.method,
                                                                                end_t, self.resolution))

        simulation_parameter_validate(end_t=end_t, initial_conditions=initial_conditions,
                                      rates_params=rate_parameters, drain_params=drain_parameters)

        def read_output(filepath):
            independent = array.array('d')
            dependent = tuple()
            label_translator = {v.replace('$', ''): k for k, v in self._simulator.internal_symbol_dict.items()}
            with open(filepath, mode="r") as rfile:
                white_space = re.compile(r"\s+")
                header = white_space.split(next(rfile).strip())
                for line in rfile:
                    splitted = array.array('d', map(float, white_space.split(line.strip())))
                    independent.append(splitted[:1][0])
                    dependent += (splitted[1:],)
            return tuple(label_translator[sym] for sym in header[1:]), independent, dependent

        def collect_multiple_output(trajectories_paths, errors=()):
            for tpath in trajectories_paths:
                try:
                    header, independent, dependent = read_output(tpath)

                    yield SimulationOutput(name, (0, end_t), header,
                                           independent=independent, dependent=dependent,
                                           solver_method=self.method, errors=errors)
                except FileNotFoundError as e:
                    yield SimulationOutput(name, (0, end_t), self._simulator.symbols,
                                           solver_method=self.method, errors=(e,) + errors)

        self.logger.info("started on StochKit2 simulation")

        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = path.join(tmp_dir, model_filename)
            model_home_dir = path.join(tmp_dir, output_dirname)
            model = self.model(initial_conditions, rate_parameters, drain_parameters)

            self.logger.info("Stochkit2 model:\n{}".format(model))
            with open(model_path, mode="w") as model_file:
                model_file.write(model)

            if self.method == StochKit2StochasticSolvers.SSA:
                program_name = "ssa"
            elif self.method == StochKit2StochasticSolvers.tauLeaping:
                program_name = "tau_leaping"
            else:
                raise util_exceptions.SimulationError("Unknown stochkit2 method selected")

            program_path = path.join(self.stochkit2_path, program_name)
            self.logger.info("Using stochkit2 driver at {}".format(program_name))
            execution_args = [program_path, '-m {}'.format(model_path),
                              '-r {}'.format(self.trajectories), '-t {}'.format(end_t),
                              '-i {}'.format(self.resolution),
                              '--epsilon {}'.format(self.tau_leaping_epsilon),
                              '--threshold {}'.format(self.switch_threshold),
                              *self.flag_options]
            self.logger.info("Execution arguments are {!r}".format(" ".join(execution_args)))

            with subprocess.Popen(" ".join(execution_args), shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, preexec_fn=os.setsid) as process:
                try:
                    output, unused_err = process.communicate(timeout=self.timeout)
                    self.logger.info(output)
                except subprocess.TimeoutExpired as exception:
                    # Time out path
                    os.killpg(os.getpgid(process.pid), signal.SIGINT)
                    messages.print_solver_done(name, self.method.name, was_failure=True)
                    try:
                        partial_trajectories = os.listdir(path.join(model_home_dir, 'trajectories'))
                    except FileNotFoundError:
                        # Error in listing trajectory files
                        messages.print_solver_done(name, self.method.name, True)
                        return SimulationOutput(name, (0, end_t), self._simulator.symbols,
                                                solver_method=self.method, errors=(exception,
                                                                                   util_exceptions.
                                                                                   SimulationError(
                                                                                       "No partial trajectories")))

                    if len(partial_trajectories) == 0:
                        # There was no trajectory files
                        messages.print_solver_done(name, self.method.name, True)
                        return SimulationOutput(name, (0, end_t), self._simulator.symbols,
                                                solver_method=self.method, errors=(exception,))
                    else:
                        # Collected from all partial trajectory files
                        messages.print_solver_done(name, self.method.name, True)
                        return SimulationOutputSet(collect_multiple_output(partial_trajectories,
                                                                           errors=(exception,)))

                if process.returncode != 0:
                    # Error in process execution
                    exception = util_exceptions.SimulationError("Error in simulation: {}".format(output.decode()))
                    messages.print_solver_done(name, self.method.name, was_failure=True)
                    return SimulationOutput(name, (0, end_t), self._simulator.symbols,
                                            solver_method=self.method, errors=(exception,))
            output_trajectories_path = path.join(model_home_dir, 'trajectories')
            trajectory_paths = tuple(os.path.join(output_trajectories_path, t)
                                     for t in os.listdir(output_trajectories_path))

            if len(trajectory_paths) != self.trajectories:
                # Partial trajectories
                with open(path.join(model_home_dir, 'log.txt')) as log:
                    log_message = log.readlines()
                    if settings.logging_is_enabled():
                        self.logger.warn(log_message)
                    if len(trajectory_paths) == 0:
                        messages.print_solver_done(name, self.method.name, True)
                        return SimulationOutput(name, (0, end_t), self._simulator.symbols,
                                                solver_method=self.method, errors=(util_exceptions
                                                                                   .SimulationError("Simulation ended "
                                                                                                    "with no output"),))
                    else:
                        messages.print_solver_done(name, self.method.name, True)
                        return SimulationOutputSet(collect_multiple_output(trajectory_paths, errors=(util_exceptions
                                                                                                     .SimulationError(
                                                                                                      log_message),),))
            elif self.trajectories == 1:
                # Only one trajectory was requested so don't pack to set
                messages.print_solver_done(name, self.method.name)
                return list(collect_multiple_output(trajectory_paths))[0]
            else:
                # We got all the trajectories!
                messages.print_solver_done(name, self.method.name)
                return SimulationOutputSet(collect_multiple_output(trajectory_paths))
